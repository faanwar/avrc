# This software is Copyright (c) 2015,
# The Regents of the University of California.
#
#
# Core Developers:
#   Ajay Mohan (ajmohan@ucsd.edu)
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

from avrc.redcross import RCProject, log, config, lookup
from datetime import datetime
from monthdelta import monthmod
import argparse, json, traceback, turbomail 
from mako import exceptions
import boto3
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

cli = argparse.ArgumentParser(description='Early Test Reminder Email')

cli.add_argument(
    '-c', '--config',
    dest='settings',
    type=config.from_file,
    metavar='FILE',
    help='Configuration File')



def send_email(template, subject, sender, receipients, ses_key_id, ses_key, type_email):
        try:
            COMMASPACE = ', '
            print(receipients)
            html_content = template
            client = boto3.client(
                'ses',
                aws_access_key_id=ses_key_id,
                aws_secret_access_key=ses_key,
                region_name="us-west-2"
            )
            # Build an email
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = COMMASPACE.join(receipients)

            msg.attach(MIMEText(html_content, type_email))
            client.send_raw_email(
                Source=sender,
                Destinations=receipients,
                RawMessage={
                    'Data': msg.as_string(),
                }
            )
        except Exception as e: 
            print(e)


def send_reminder(settings):
  """ 
      Parameters: 
            
            buckets: Dict of site codes and list of Results for that site as key, value pairs
            
            settings: A dictionary of settings specified in the configuration file            
      Returns None
  """
  try:
    log.info("Early Test Email Alerts are about to be sent")
    ses_key_id = settings['ses_key_id']
    ses_key = settings['ses_key']
    rcs = json.loads(open(settings['redcap_json'], 'r').read())
    
    # Read from the configuration files    
    rem_keys = settings['rem.codes'].split() 
    
    pat_keys = settings['pat.codes'].split()

    keys = rem_keys + pat_keys

    months_to_notify = int(settings['months.tonotify'])
  
    # Connect to all the required projects in RedCAP    
    redcap = RCProject(keys, rcs)
    staff_emails = get_receipients(redcap, '1')
    staff_emails_other = get_receipients(redcap, '2')

    #send other email reminders
    sdun_patient_count, sdun_emails_sent, sdun_invalid_emails_count = send_reminder_single(ses_key_id, ses_key, settings, staff_emails_other, months_to_notify)
    er_patient_count, er_emails_sent, er_invalid_emails_count, asr_patient_count, asr_emails_sent, asr_invalid_emails_count  = send_reminder_etc(ses_key_id, ses_key, settings, staff_emails_other, months_to_notify)

    # Required Patient Fields
    pfields = ['et_pid','rc_id', 'phone1','phone2','email1','email2', 'first_name', 'last_name']
    precords = {}
    text = lookup.get_template('email/reminder.mako').render(**template_input)
    send_email(text, "UCSD Early Test - Good to Go reminders", "UCSD - Good to Go<" + settings["remind.email"] + ">", "fakhra.anwer@gmail.com", ses_key_id, ses_key, "html")
    break
    for key in pat_keys:
      precords[key] = redcap.project[key].export_records(fields=pfields)
      

    # This dictionary holds a map of Patient email to a list of
    # rc_ids of that specific patient
    # NOTE: The rc_ids may also belong to multiple sites.
    hash_email = {}

    # This is a dictionary to the email ids of patients to their names
    hash_names = {} 

    # This dictionary will hold the list of rcid to specific 
    # sites, and therefore prevent multiple calls to the
    # RedCAP rest APIs.
    site_rcid = {}    

    for site in rem_keys:
      site_rcid[site] = []
   
    
    # Today we have a single redcap project for patients. In the future
    # there can be multiple projects for patients. The below code will 
    # still work and have a better performance.
    
    import sys
    for pat_key, pat_records in precords.iteritems():
      log.debug("Total of patient records in %s =  %d", pat_key, len(pat_records)) 
      log.debug("The size of the records: %d Bytes", sys.getsizeof(pat_records))

      # Patient Records that need to be updated
      # with working primary email for this site 
      to_update = []
      invalid_emails = {}
      for patient in pat_records:
        try:

          # Extract Site information
          #site = patient['rc_id'].upper()         

          # The testing site visited by this patient is not configured 
          # to send email reminders. So continue to the next patient
          #if site.startswith(tuple(rem_keys)) == False:
            #continue
          if patient['email1'] == '':
            # ignore patients for whom we don't have email IDs
            if patient['email2'] == '':
              continue
            else:
              # Set the primary email and delete the secondary
              patient['email1'] = patient['email2']
              patient['email2'] = ''
              to_update.append(patient)
          
          if patient['et_pid'] in hash_email:
            continue
          else:
            hash_email[patient['et_pid']] = [patient['email1']]
            hash_names[patient['et_pid']] = { 'first_name' : patient['first_name'],
                                              'last_name' : patient['last_name'] 
                                            }

          #site_rcid[patient['rc_id'][:-5]].append(patient['rc_id'])
        except KeyError as e:
          log.critical(traceback.format_exc())
          pass

  
      """if len(to_update) > 0:
        try:
          #updated_count = redcap.project[pat_key].import_records(to_update)
          log.debug(" %d Emails needed to be moved from email2 to email1 for %s", len(to_update), pat_key)
        except:
          log.critical(traceback.format_exc())
          pass"""

      # Some stats to log
      log.debug("Unique Patient with email Ids: %d", len(hash_email.keys()))
      #for email, visits in hash_email.iteritems():
      #  log.debug("Patient Email: %s, Number of Visits: %d", email, len(visits))

      #History of the patients as a list returned by redcap
      patient_history = []

      # We need the following fields to decide if we need to send emails for this patient
      fields = ['et_pid','rc_id','visit_date','rapid1', 'rapid2', 'testing_reminder','dhiv', 'lstremndr_dt']
      #for site, records in hash_email.iteritems():
      patient_history.extend(redcap.project['SDET'].export_records(fields=fields))
      patient_history.extend(redcap.project['76C'].export_records(fields=fields))
      log.debug("Total Patient history to Process:%d", len(patient_history))

      # Patient history modified data structure for convenience
      hist_map = {}
      for history in patient_history:
        hist_map[history['rc_id']] = history
 
      count = 0
      for key, val in hash_email.iteritems():
        print 'key'
        print key
        print 'value'
        print val
        latest_record  = None
        # At the end of the following loop, record will consists of the latest visit
        # information for this patient.(Indicated by the email string 'key')
        skip = False
        for rc_id, visit_val in hist_map.iteritems():
          try:
            if visit_val['et_pid'] != key:
              continue
            if visit_val['visit_date'] == '':
              continue
            print 'visit date exists'
            print 'rcid'
            print rc_id 
            print 'visit'
            print visit_val
            visit = datetime.strptime(visit_val['visit_date'],
                                      "%Y-%m-%d")
            if latest_record == None:
              latest_record = visit_val
            else:
              latest_date= datetime.strptime(latest_record['visit_date'],"%Y-%m-%d") 
              if latest_date <= visit:
                print 'compare dates'
                print visit
                print latest_date
                latest_record = hist_map[rc_id]
          except KeyError:
            log.critical(traceback.format_exc())


        print 'latest record'
        print latest_record
        if latest_record == None:
          continue
        notify, months = is_reminder_required(latest_record, months_to_notify)
        if notify == True:
          print 'patient email process initiated ' + hash_names[key]['first_name']
          # We could send messages in bulk if it had a common body. But since the body is
          # unique for every recipient we have to go through the non-performant process
          # of sending one email at a time
          template_input = { 'username'         : hash_names[key]['first_name'],
                             'months'           : months,
                             'visit_date'       : latest_record['visit_date'],
                             'ltw_url'          : settings['ltw_url'],
                             'unsubscribe_url'  : settings['unsubscribe_url'] + '?email='+ val[0] +"&rc_id=" + latest_record['rc_id'] + "&unsubscribe.submitted=Unsubscribe",
                             'phone'            : settings['phone'],
                             'email'            : val[0]
                            }
          try:
            #turbomail.send(turbomail.Message(
            #              author="UCSD - Good to Go<" + settings["remind.email"] + ">",
            #              organization=["UCSD - Good to Go"],
            #              bcc=[key],
            #              reply_to=settings["remind.email"],
            #              subject="UCSD Early Test - Good to Go reminders",
            #              rich = lookup.get_template('email/reminder.mako').render(**template_input),
            #              headers =  {'list-unsubscribe': "<" + template_input['unsubscribe_url'] 
            #                                                   + ">,<mailto:" + settings["remind.email"] +">"},
            #              plain = "this is a reminder email to complete early test at " + settings['ltw_url']))
            p_email = []
            p_email.append(val[0])
            text = lookup.get_template('email/reminder.mako').render(**template_input)
            send_email(text, "UCSD Early Test - Good to Go reminders", "UCSD - Good to Go<" + settings["remind.email"] + ">", "fakhra.anwer@gmail.com", ses_key_id, ses_key, "html")
            break
            count = count + 1
            match = next(d for d in patient_history if d['rc_id'] == latest_record['rc_id'])
            print 'patient email date record '
            print match
            #if match != '':
              #match['lstremndr_dt'] = datetime.today().date().strftime('%Y/%m/%d')
              
          except:
            invalid_emails[latest_record['et_pid']] = val[0]
            log.critical(traceback.format_exc())
            pass
        
      try:
        #redcap.project[site].import_records(patient_history)
        print 'patient email date updated'
      except:
          pass
      # Delete invalid email Ids from redcap. A hashSet is handy for this operation
      # invalid_emails = set(invalid_emails)
    
      invalid_emails_count = len(invalid_emails.keys())

      if invalid_emails_count > 0:
        with open('/var/tmp/invalid_emails_'+ pat_key + str(datetime.today().date()), 'wr+') as f:
          json.dump(invalid_emails, f)
    
      """ This logic will be commented out, until the script is mature 
      and all other features are well tested

      # Remove wrong email ids from redcap
      for pat_key, pat_records in precords.iteritems():
        try:
          to_update = []
          for patient in pat_records:
            if patient['email1'] in invalid_emails:
              patient['email1'] = ''
              to_update.append(patient)
              log.debug("Rcid: %s, Email: %s is removed as invalid from redcap", patient['rc_id'], patient['email1'])         
          updated_count = redcap.project[pat_key].import_records(to_update)
      
        except Exception as e:
          log.critical
          pass
      """
      log.debug("Total Emails sent out today:%d", count)
      print 'data'
      print len(hash_email.keys())
      print count
      print invalid_emails_count
      print staff_emails
      stats = {
             'date': datetime.today().date(),
             'sdet_patient_count': len(hash_email.keys()),
             'sdet_emails_sent': count,
             'sdet_invalid_emails_count':invalid_emails_count,
             'sdun_patient_count' : sdun_patient_count,
             'sdun_emails_sent' : sdun_emails_sent,
             'sdun_invalid_emails_count' : sdun_invalid_emails_count,
             'asr_patient_count' : asr_patient_count,
             'asr_emails_sent' : asr_emails_sent,
             'asr_invalid_emails_count' : asr_invalid_emails_count,
             'er_patient_count' : er_patient_count,
             'er_emails_sent' : er_emails_sent,
             'er_invalid_emails_count' : er_invalid_emails_count
            }      
      try:
        text = lookup.get_template('email/stats.mako').render(**stats)
        #turbomail.send(turbomail.Message(
        #                author = "UCSD - Good to Go<" + settings["remind.email"] + ">",
        #                organization = ["UCSD - Good to Go"],
        #                to = staff_emails,
        #                reply_to = settings["remind.email"],
        #                subject = "Good to Go Email Reminders Statistics",
        #                plain = text))
        
        #send_email(text, "SDET: Good to Go Email Reminders Statistics", "UCSD - Good to Go<" + settings["remind.email"] + ">", staff_emails, ses_key_id, ses_key, "plain")
        #send_email(text, "Good to Go Email Reminders Statistics", "UCSD - Good to Go<" + settings["remind.email"] + ">", staff_emails, ses_key_id, ses_key, "plain")

      except:
        log.debug(lookup.get_template('email/stats.mako').render(**stats))
        log.critical(traceback.format_exc())

  except: 
    log.critical(traceback.format_exc())
    turbomail.send(turbomail.Message(
        to=settings['notify.error'].split(),
        subject='[Early Test Reminders]:There is an exception in sending out monthly reminders!',
        plain=traceback.format_exc()))

def is_reminder_required(record, months_to_notify):
  """
    Input
      record: A dictionary of key rcid to value of a subset of fields from the redcap db
  
    Output
      boolean: True/False based on satisfying the condition to email 
  """
  try:
    if record['lstremndr_dt'] == datetime.today().date().strftime('%Y/%m/%d'):
      print 'already sent'
      return False, 0
    if record['testing_reminder'] !=  u'1':
      # if the patient had opted out of reminders Don't bother further condtions
      return False, 0
    elif (record['rapid1'] is u'1' and record['rapid2'] is not u'0') or record['dhiv'] is u'P':
      # The above condition is true for positive patients
      # Since positive patients will be going through
      # a different treatment plan, they dont need to
      # be reminded for testing. So return false
      # The values meani, 0-Negative 1-Positive 2-Indeterminate
      return False, 0
    else: 
      current_date = datetime.today() 
      visit_date = datetime.strptime(record['visit_date'],"%Y-%m-%d")
      year = visit_date.year
      current_year = current_date.year
      limit_year = current_year - 2
      print(limit_year)
      if year < limit_year:
        return False,0
      month, days = monthmod(visit_date, current_date)
      # Now, if record has a visit date that falls in to you notification slab,
      # Then this email Id should be notified
      if month.months >= months_to_notify:
        if visit_date.month in companion_months(current_date.month):
          return True, month.months

  except:
    #Ignore if we don't have the user information for the rcid
    log.critical(traceback.format_exc())
  
  return False, 0

# This function returns companion months of the year 
# to send updates for. If you run this script in Jan,
# you will be returned Jan, May and December
# (ofcourse have to used for the previous years)
def companion_months(month=None):
  if month in (1, 5, 9):
    return (1,5,9)
  elif month in (2, 6, 10):
    return (2,6,10)
  elif month in (3, 7, 11):
    return (3,7,11)
  else:
    return (4,8,12)
   
def get_receipients(redcap, code):
  email_list = []
  records = redcap.project['Email'].export_records()
  for record in records:
    if record['et_mail_stats'] == code or record['et_mail_stats'] == '3':
      email_list.append(record['email'])
  return email_list

def send_reminder_statistics(settings, key, patient_count, emails_sent, invalid_emails_count, staff_emails, ses_key_id, ses_key):
  if key == 'ASR':
    key = "AVRC Screening Registry"
  elif key == 'ER':
    key = "Email Registry"
  log.debug("Total Emails sent out today: " + key)
  stats = {
          'date': datetime.today().date(),
          'patient_count': patient_count,
          'emails_sent': emails_sent,
          'invalid_emails_count':invalid_emails_count
        }      
  try:
    text = lookup.get_template('email/stats.mako').render(**stats)
    #send_email(text, key + ": Good to Go Email Reminders Statistics", "UCSD - Good to Go<" + settings["remind.email"] + ">", staff_emails, ses_key_id, ses_key, "plain")
    send_email(text, ": Good to Go Email Reminders Statistics", "UCSD - Good to Go<" + settings["remind.email"] + ">", "fakhra.anwer@gmail.com", ses_key_id, ses_key, "plain")

  except:
    log.debug(lookup.get_template('email/stats.mako').render(**stats))
    log.critical(traceback.format_exc())

def send_reminder_single(ses_key_id, ses_key, settings, staff_emails, months_to_notify):
  try:
    
    log.info("Early Test Single Email Alerts are about to be sent")

    sdun_patient_count= sdun_emails_sent= sdun_invalid_emails_count = 0

    rcs = json.loads(open(settings['redcap_json'], 'r').read())
    
    keys = settings['single_email.code'].split()

    redcap = RCProject(keys, rcs)

    fields = ['rc_id','visit_date','rapid1', 'rapid2', 'testing_reminder','dhiv', 'first_name', 'last_name', 'email1', 'phone1']
    for key in keys:
      invalid_emails_count = 0
      emails_sent = 0
      patient_count = 0
      arecords = redcap.project[key].export_records()
      for record in arecords:
        patient_count = patient_count +1
        notify, months = is_reminder_required(record, months_to_notify)
        if notify == True and record['email1'] != '':
          print 'patient email process single email initiated ' + record['first_name']
          
          template_input = { 'username'         : record['first_name'],
                              'visit_date'       : record['visit_date'],
                              'ltw_url'          : settings['ltw_url'],
                              'phone'            : settings['phone'],
                              'email'            : record['email1']
                            }
          try:
            p_email = []
            p_email.append(record['email1'])
            text = lookup.get_template('email/reminder_etc.mako').render(**template_input)
            #send_email(text, "UCSD Early Test - Good to Go reminders", "UCSD - Good to Go<" + settings["remind.email"] + ">", p_email, ses_key_id, ses_key, "html")
            emails_sent = emails_sent +1
          except:
            invalid_emails_count = invalid_emails_count +1
            log.critical(traceback.format_exc())
            pass
      if key == 'SDUN':
        sdun_patient_count = patient_count
        sdun_emails_sent = emails_sent
        sdun_invalid_emails_count  = invalid_emails_count
        print 'SDUN'
        print patient_count
        print emails_sent
        print invalid_emails_count
      #send_reminder_statistics(settings, key, patient_count, emails_sent, invalid_emails_count, staff_emails, ses_key_id, ses_key)
    return sdun_patient_count, sdun_emails_sent, sdun_invalid_emails_count
  except:
    #Ignore if we don't have the user information for the rcid
    log.critical(traceback.format_exc())
  
  return 0,0,0

def send_reminder_etc(ses_key_id, ses_key, settings, staff_emails, months_to_notify):
  try:
    log.info("Early Test ETC Email Alerts are about to be sent")
    er_patient_count= er_emails_sent= er_invalid_emails_count= asr_patient_count= asr_emails_sent= asr_invalid_emails_count = 0
    rcs = json.loads(open(settings['redcap_json'], 'r').read())
    
    a_keys = settings['avrc_email.code'].split()
    e_keys = settings['etc_email.code'].split()
    # Connect to all the required etc projects in RedCAP    
    a_redcap = RCProject(a_keys, rcs)
    e_redcap = RCProject(e_keys, rcs)

    # Required Patient Fields
    a_fields = ['consent_date', 'other_phone','email','current_hiv', 'fname', 'lname', 'testing_reminder']
    e_fields = ['collect_date', 'phone', 'email', 'first_name', 'last_name']
    arecords = {}
    erecords = {}

    #AVRC Screening Registry  
    for key in a_keys:
      invalid_emails_count = 0
      emails_sent = 0
      patient_count = 0
      arecords = a_redcap.project[key].export_records(fields=a_fields)
      print(arecords)
      for record in arecords:
        patient_count = patient_count+1
        notify, months = is_reminder_required_screening(record, months_to_notify)
        if notify == True and record['email'] != '':
          print 'patient email process avrc screening registry initiated ' 
          
          template_input = { 'username'         : record['fname'],
                              'visit_date'       : record['consent_date'],
                              'ltw_url'          : settings['ltw_url'],
                              'phone'            : settings['phone'],
                              'email'            : record['email']
                            }
          try:
            p_email = []
            p_email.append(record['email'])
            text = lookup.get_template('email/reminder_etc.mako').render(**template_input)
            #send_email(text, "UCSD Early Test - Good to Go reminders", "UCSD - Good to Go<" + settings["remind.email"] + ">", p_email, ses_key_id, ses_key, "html")
            emails_sent = emails_sent +1
          except:
            invalid_emails_count = invalid_emails_count +1
            log.critical(traceback.format_exc())
            pass
      #send_reminder_statistics(settings, key, patient_count, emails_sent, invalid_emails_count, staff_emails, ses_key_id, ses_key)
      asr_patient_count = patient_count
      asr_emails_sent = emails_sent
      asr_invalid_emails_count  = invalid_emails_count
      print 'ASR'
      print patient_count
      print emails_sent
      print invalid_emails_count
    #Email Registry
    for key in e_keys:
      invalid_emails_count = 0
      emails_sent = 0
      patient_count = 0
      erecords = e_redcap.project[key].export_records(fields=e_fields)
      for record in erecords:
        patient_count = patient_count +1
        notify, months = is_reminder_required_etc(record, months_to_notify)
        print(record)
        if notify == True and record['email'] != '':
          print 'patient email process email registry initiated ' 
          
          template_input = { 'username'         : record['first_name'],
                              'visit_date'       : record['collect_date'],
                              'ltw_url'          : settings['ltw_url'],
                              'phone'            : settings['phone'],
                              'email'            : record['email']
                            }
          try:
            p_email = []
            p_email.append(record['email'])
            text = lookup.get_template('email/reminder_etc.mako').render(**template_input)
            #send_email(text, "UCSD Early Test - Good to Go reminders", "UCSD - Good to Go<" + settings["remind.email"] + ">", p_email, ses_key_id, ses_key, "html")
            emails_sent = emails_sent +1
          except:
            invalid_emails_count = invalid_emails_count +1
            log.critical(traceback.format_exc())
            pass
      #send_reminder_statistics(settings, key, patient_count, emails_sent, invalid_emails_count, staff_emails, ses_key_id, ses_key)
      er_patient_count = patient_count
      er_emails_sent = emails_sent
      er_invalid_emails_count  = invalid_emails_count
      print 'ER'
      print patient_count
      print emails_sent
      print invalid_emails_count
    return er_patient_count, er_emails_sent, er_invalid_emails_count, asr_patient_count, asr_emails_sent, asr_invalid_emails_count
  except:
    #Ignore if we don't have the user information for the rcid
    log.critical(traceback.format_exc())
  
  return 0, 0, 0 , 0 , 0 ,0

def is_reminder_required_etc(record, months_to_notify):

  try:
    current_date = datetime.today() 
    visit_date = datetime.strptime(record['collect_date'],"%Y-%m-%d")
    
    month, days = monthmod(visit_date, current_date)
    # Now, if record has a visit date that falls in to you notification slab,
    # Then this email Id should be notified
    if month.months >= months_to_notify:
      if visit_date.month in companion_months(current_date.month):
        return True, month.months

  except:
    #Ignore if we don't have the user information for the rcid
    log.critical(traceback.format_exc())
  
  return False, 0

def is_reminder_required_screening(record, months_to_notify):

  try:
    if record['testing_reminder'] !=  u'1':
      return False, 0
    elif record['current_hiv'] is u'1':
      return False, 0
    else: 
      current_date = datetime.today() 
      visit_date = datetime.strptime(record['consent_date'],"%Y-%m-%d")
      
      month, days = monthmod(visit_date, current_date)
      # Now, if record has a visit date that falls in to you notification slab,
      # Then this email Id should be notified
      if month.months >= months_to_notify:
        if visit_date.month in companion_months(current_date.month):
          return True, month.months

  except:
    #Ignore if we don't have the user information for the rcid
    log.critical(traceback.format_exc())
  
  return False, 0




def main():
  try:
    args = cli.parse_args()
    settings = args.settings

    send_reminder(settings)
     
  except Exception as e:
    log.critical(traceback.format_exc())
    turbomail.send(turbomail.Message(
        to=settings['notify.error'].split(),
        subject='[The Early Test]: Reminder Email Exception!',
        plain=traceback.format_exc()))

if __name__ == "__main__":
  main()  
