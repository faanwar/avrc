# This software is Copyright (c) 2015,
# The Regents of the University of California.
#
# Developed by the UCSD CFAR BIT Core (bitcore@ucsd.edu)
#
# Core Developers:
#   Sergei L Kosakovsky Pond (spond@ucsd.edu)
#   Jason A Young (jay007@ucsd.edu)
#   Marco A Martinez (mam002@ucsd.edu)
#   Steven Weaver (sweaver@ucsd.edu)
#
# Significant contributions from:
#   David Mote (davidmote [at] gmail [dot] com)
#   Jennifer Rodriguez-Mueller (almostlikethat [at] gmail [dot] com)
#   Drew Allen (asallen@ucsd.edu)
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
# LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
# SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
# INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
# CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
# ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.

import datetime
from pyramid.httpexceptions import HTTPFound
from avrc.redcross import models, RCProject
from aeh.earlytest import Session, Config, log, mail_settings
from aeh.earlytest.models import RootFactory
from pyramid.security import has_permission
import requests
from aeh.earlytest import redcap_settings as rcs, Config
import traceback, json
import turbomail

# get_otp(rc_id)
# Purpose: This function accpets an rcid as a string. Uses it to query the 
# patients database and get their phone numbers. And uses the phone number 
# to generate a OTP using textbelt REST API

# parse_input(text)
# Purpose: This function accepts a string, removes all whitespaces, strips the string into the
# site code and reference number. It returns a dictionary with the site code and reference number.
def parse_input(text):
    strip_text = text.replace(' ','')
    offset = len(strip_text) - 5
    site_code = strip_text[:offset].upper()
    ref_num   = strip_text[offset:]

    return { 'site_code': site_code, 'ref_num': ref_num }

# get_fullname(clean_input)
# Purpose: This function returns the full red cross id (site_code + ref_num) as a string
def get_fullname(clean_input):
    return clean_input['site_code'] + clean_input['ref_num']


# process(request, default_view={})
# Purpose: This function looks at the user's first and second RCID inputs and determines
# the most appropriate response. All the possible responses are present in the HTML template
# but they are only made visible depending on the value of query_status and query_debug.
# RESULTS_NOT_FOUND = Result for this RCID not found in database
# RESULTS_NOT_AVAILABLE = Client is HIV positive, or result does not have a draw date
# QUERY_INVALID = RCID1 and RCID2 did not match
# RESULTS_NEGATIVE = Client is HIV negative, draw date is at least 14 days old, and draw date is
# less than 90 days old
# RESULTS_OUT_OF_DATE = Draw date is more than 90 days old
def process(request, default_view={}):
    """
    Process query for test results
    """
    # Grabs configuration to set expiration of test results and buffer time 
    days_til_exp = Config.getint('aeh:results', 'results_expiration')
    days_til_access = Config.getint('aeh:results', 'results_buffer')
    site_code_list = Config.get('aeh:results', 'site.codes').upper().split()
    default_number = '76C##### or 76GH##### or 76FJ#####'

    query_status = ""
    clean_input1 = {'site_code':'', 'ref_num':''}
    clean_input2 = {'site_code':'', 'ref_num':''}

    query_draw_date = ""
    rc_id = "12345678"
    otp = None
    show_otp = False

    ret = {
      'defaultNumber': default_number,
      'queryDebug': False,
      'queryStatus' : query_status,
      'cleanNumber1': get_fullname(clean_input1),
      'cleanNumber2': get_fullname(clean_input2),
      'queryTestDate': query_draw_date,
    }
    return dict(default_view.items() + ret.items())

def is_otp_sent(rcid, mode, contact):
    try:              
      if contact is '' or contact == None:
        raise  
        
      if mode == 'EMAIL' or Config.getboolean('aeh:results', 'otp_mock') == True :
        phone = Config.get('aeh:results','otp_mock_phone') 
      else:
        phone = contact
               
      #og.info("Phone number is:%s", phone)
      Response = requests.post(Config.get('aeh:results','otp_gen_url'), {
                              'phone': phone,
                              'userid': rcid,
                              'lifetime': Config.get('aeh:results', 'otp_lifetime'),
                              'key': Config.get('aeh:results', 'otp_key')})
                              
      status = json.loads(Response.text)
      #log.info(Response.text)
      # Textbelt doesn't email otps we do it
      if mode == 'EMAIL' and status['success'] == True:
        turbomail.send(turbomail.Message(
                        author = "ucsd - leadtheway<" + mail_settings["remind.email"] + ">",
                        organization = ["ucsd - leadtheway"],
                        bcc = [contact],
                        subject = "Your Verification Code",
                        reply_to = mail_settings["remind.email"],
                        plain = "Your verification code for access is " + status['otp'] + "."))
      
      return status['success'], status

    except:
      #log.critical(traceback.format_exc())
      return False, None

def is_otp_valid(otp, rcid):

    try:
      Response = requests.get(Config.get('aeh:results','otp_verify_url'),{
                             'otp': otp,
                             'userid': rcid,
                             'key': Config.get('aeh:results','otp_key')})
      status = json.loads(Response.text)
      #log.info("OTP Verification Status: %s", status)
      if status['success'] == True:
        return status['isValidOtp']
    except:
      pass
      #log.critical(traceback.format_exc())
    return False

def get_patient(rc_id):
    try:
      patient = None
      patient_sites = Config.get('aeh:results','pat.codes').split()   
      #log.info(patient_sites)
      redcap = RCProject(patient_sites, rcs)
      for key in patient_sites:
        try:
          patients = redcap.project[key].export_records(records=[str(rc_id)])
          patient = patients[0]
          #log.info(patient)
          return patient
        except:
          #log.info(traceback.format_exc())
    except:
	  #log.info(traceback.format_exc())

def find_phone_email(clean_rcid):
    status = 'QUERY_INVALID'
    phone = None
    email = None
    if clean_rcid != None:
      patient = get_patient(clean_rcid)
      if patient != None:
        phone = patient['phone1'] if patient['phone1'] != "" else patient['phone2']
        email = patient['email1'] if patient['email1'] != "" else patient['email2']
        
        # Atleast one is essential      
        if (phone is None or phone is "") and (email is None or email is ""):
          status = 'NO_CONTACT'            
        elif (phone is not None or phone is not "") and (email is not None or email is not ""):
          status = 'BOTH' 
        elif phone is None or phone is "":
          status = 'EMAIL'
        else:
          status = 'PHONE'
    #log.info("In find phone email: Phone: %s, Email: %s, Status: %s \n", phone, email, status) 
    return phone, email, status

    
def otp(request, admin, default_view={}):
    try:
      phone, email, clean_rcid = None, None, None
      otp_status = 'NON_VALIDATED'
      queryStatus = 'QUERY_INVALID'
      mode, show_barker = '', ''
 
      if 'clean_rcid' in request.params:
        clean_rcid = request.params['clean_rcid']
        #log.info("Current rcid:%s",clean_rcid)
      
      if 'userInput1' in request.POST and 'userInput2' in request.POST:

        # parse inputs for site_code and reference_number
        clean_input1 = request.POST['userInput1']
        clean_input2 = request.POST['userInput2']

        # Check if input 1 and input 2 match
        if clean_input1 != clean_input2 or clean_input1 == "":
            query_status = 'QUERY_INVALID'
            show_barker = 'ERROR'   
            ret = {
                    'otp_status': otp_status,
                    'clean_rcid': clean_rcid,
                    'queryStatus' : queryStatus,
                    'phone': phone,
                    'email': email,
                    'mode' : mode,
                    'show_barker': show_barker
                  }
            
            return dict(default_view.items() + ret.items()) 
            
      if admin != True:  
        if "PHONE" in request.params:
          mode = 'PHONE'
          email = None
        elif "EMAIL" in request.params:
          mode = 'EMAIL'
          phone = None

        if mode != '':
          otp_status = 'VALIDATING'
          cp_phone, cp_email, cnxn = find_phone_email(clean_rcid)
          if mode == 'PHONE':
            contact = cp_phone
          else:
            contact = cp_email
            
          sent, text_status = is_otp_sent(clean_rcid, mode, contact)
          #log.info("OTP sent: %ss, text_status: %s", sent , text_status)
          cp_phone, cp_email = masked_contacts(cp_phone, cp_email)
          
          
          if phone == None:
            email = cp_email
          elif email == None:
            phone = cp_phone
          #log.info("Phone: %s, Email: %s, Status: %s \n", phone, email, cnxn) 
          show_barker = 'OTP_PROMPT'

        #log.info("Mode: %s, Otp_Status: %s \n", mode, otp_status)
        if otp_status == 'NON_VALIDATED' and "userInput1" in request.params:
            clean_rcid = request.params['userInput1'] 
            phone, email, cnxn = find_phone_email(clean_rcid) 
            #log.info("Phone: %s, Email: %s, Status: %s \n", phone, email, cnxn) 
            if cnxn is 'NO_CONTACT' or cnxn is 'QUERY_INVALID':
              show_barker = 'ERROR'
              queryStatus = cnxn 
            else:
              phone, email = masked_contacts(phone, email)
              show_barker = 'GENERATE_OTP'
              #log.info("Phone: %s, Email: %s,\n", phone, email)
        
        if "otp" in request.params:
            otp = request.params['otp']

            if clean_rcid == None:
                otp_status = 'NON_VALIDATED'
                show_barker = 'NO_RCID'
            # Add logic to verify otp
            elif is_otp_valid(otp, clean_rcid) ==   True:
              otp_status = 'VALIDATED'
              show_barker = 'RESULTS'
            else:
              otp_status = 'INVALID'
              queryStatus = ''
              show_barker = 'ERROR'
      else:
        #Admin users come from userInput1
        if 'userInput1' in request.params:
            clean_rcid = request.params['userInput1'] 
            otp_status = 'VALIDATED'
            show_barker = 'RESULTS'
        else:
            show_barker = 'NO_RCID'
            otp_status = 'NON_VALIDATED'
            
        
      if otp_status == 'VALIDATED':
          queryStatus = get_results(clean_rcid)

    except:
      #log.info(traceback.format_exc())
      raise
    
    ret = {
        'otp_status': otp_status,
        'clean_rcid': clean_rcid,
        'queryStatus' : queryStatus,
        'phone': phone,
        'email': email,
        'mode' : mode,
        'show_barker': show_barker
    }
    #log.info(str(ret))
    return dict(default_view.items() + ret.items())

    
def otp_entry(request, default_view={}):
    try:
      root = RootFactory(request)
      admins  = bool(has_permission('admins', root, request))
      return otp(request,admins, default_view)
    except:
      #log.info(traceback.format_exc())
      return HTTPFound(request.route_path('results'))

def get_results(input_rcid):
       
        # parse inputs for site_code and reference_number
        clean_rcid = parse_input(input_rcid)
        
        site_code = clean_rcid['site_code']
        ref_num   = clean_rcid['ref_num']
        current_time  = datetime.date.today()
    	# Var used to determine expiration of test results
    	results_expiration = current_time - datetime.timedelta(days=int(Config.get('aeh:results', 'results_expiration')))
    	# Var used to calculate buffer time for test result retrieval
    	results_buffer = current_time - datetime.timedelta(days=int(Config.get('aeh:results', 'results_buffer')))

        site_code_list = Config.get('aeh:results', 'site.codes').split()
        if not site_code in site_code_list:
            query_status = 'RESULTS_NOT_FOUND'
        else:
            session  = Session()
            result   = session.query(models.Result)\
                         .filter(models.Result.site_code == site_code)\
                         .filter(models.Result.reference_number == ref_num).first()

            show_results = Config.getboolean('aeh:results', 'site.{0}.show_results'.format(site_code.upper()))
              
            if result and show_results:
                query_draw_date = result.draw_date
                """ 
		        Conditions to not show results 
		        a) the site doesn't allows access.
	            b) No draw date
		        c) DHIV result is P
		        """
                query_status = 'RESULTS_NOT__AVAILABLE'
                # Check if dhiv result in N
                if result.check('dhiv') is False:
                    # Check if draw date is 14 or more days
                    if query_draw_date <= results_buffer:
                        # Check if draw date is less than 90 days old
                        if query_draw_date > results_expiration:
                            query_status = 'RESULTS_NEGATIVE'
                        else:
                            query_status = 'RESULTS_OUT_OF_DATE'
            else:
                query_status = 'RESULTS_NOT_FOUND'
        
        return query_status

def masked_contacts(phone, email):
    if phone != None:
      phone = ''.join(c for c in phone if c.isdigit())
      if len(phone) == 10:
        # Gimmicks to convert to 123-456-7890 => XXX-XXX-X890
        phone = "XXX-XXX-X" + phone[-3:]
      else:
        phone = None

    if email != None:
      email_parts = email.split('@')
      if len(email_parts) < 2:
        email = None
      else:
        # Gimmicks to convert username@provider.com => uXXXXXXX@provider.com
        email = email[0] + 'X' * (len(email_parts[0])-1) + '@' + email_parts.pop()

    return phone, email
