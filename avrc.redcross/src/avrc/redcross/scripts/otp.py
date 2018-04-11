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
import requests, time

cli = argparse.ArgumentParser(description='Early Test Reminder Email')

cli.add_argument(
    '-c', '--config',
    dest='settings',
    type=config.from_file,
    metavar='FILE',
    help='Configuration File')

def is_otp_sent(patient, settings):
    try:
      phone = patient['phone1'] if patient['phone1'] != None else patient['phone2']
      email = patient['email1'] if patient['email1'] != None else patient['email2']
      Response = requests.post(settings['otp_gen_url'], {
                              'phone': phone,
                              'userid': email,
                              'key': settings['otp_key']})

      status = json.loads(Response.text)
      log.info("OTP request status: %s",status )
      return status['success'], status

    except:
      log.critical(traceback.format_exc())
      return False, None

def get_patient(rc_id, settings):
    try:
      log.info("Enter Get_Patient")
      patient = None
      rcs = json.loads(open(settings['redcap_json'], 'r').read())

      patient_sites = settings['pat.codes'].split()
    
      redcap = RCProject(patient_sites, rcs)
      for key in patient_sites:
        try:
          patients = redcap.project[key].export_records(records=[rc_id])
          patient = patients[0]
          break      

        except IndexError:
          pass

    except:
      log.critical(traceback.format_exc())
    
    log.info("Exit Get_Patient")
    return patient

def is_otp_valid(otp, patient, settings):

    try:
      email = patient['email1'] if patient['email1'] != None else patient['email2']
      Response = requests.get(settings['otp_verify_url'],{
                             'otp': otp,
                             'userid': email,
                             'key': settings['otp_key']})
      status = json.loads(Response.text)
      log.info("OTP Verification Status: %s", status)       
      if status['success'] == True:
        return status['isValidOtp']

    except:
      log.critical(traceback.format_exc())
    
    return False

def main():
  try:
    args = cli.parse_args()
    settings = args.settings
    
    if settings['otp_mock'] == 'true':
      patient = get_patient(settings['otp_mock_rcid'], settings)
      patient['phone1'] = settings['otp_mock_phone']
      log.info("Patient Info: %s", patient)
      sent_otp, status = is_otp_sent(patient, settings)
      if sent_otp == True:
        log.info("Intentional %d sec delay", 15)
        time.sleep(15)
        if is_otp_valid(str(status['otp']), patient, settings) == True:
          log.info("Successful OTP Verfication. OTP: %s", status['otp'])
        else:
          raise Exception("Invalid OTP")
      else:
        raise Exception("OTP not sent!")
       
  except Exception as e:
    log.critical(traceback.format_exc())
    turbomail.send(turbomail.Message(
        to=settings['notify.error'].split(),
        subject='[Early Test]: OTP Exception',
        plain=traceback.format_exc()))

if __name__ == "__main__":
  main()  
