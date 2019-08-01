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
import boto

cli = argparse.ArgumentParser(description='Early Test Reminder Email')

cli.add_argument(
    '-c', '--config',
    dest='settings',
    type=config.from_file,
    metavar='FILE',
    help='Configuration File')

def send_email(template, values, subject, sender, receipients):
        try:
            COMMASPACE = ', '
            print(template)
            print(receipients)
            print(values)
            html_content = render_to_string(template, values)
            client = boto.client(
                'ses',
                aws_access_key_id='AKIAIDYGCDNCKKPD6O5A',
                aws_secret_access_key='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',
                region_name="us-west-2"
            )
            # Build an email
            msg = MIMEMultipart()
            msg['Subject'] = subject
            msg['From'] = sender
            msg['To'] = COMMASPACE.join(receipients)

            msg.attach(MIMEText(html_content, 'html'))
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
    
    rcs = json.loads(open(settings['redcap_json'], 'r').read())
    
    # Read from the configuration files    
    rem_keys = settings['rem.codes'].split() 
    
    pat_keys = settings['pat.codes'].split()

    keys = rem_keys + pat_keys

    months_to_notify = int(settings['months.tonotify'])
  
    # Connect to all the required projects in RedCAP    
    redcap = RCProject(keys, rcs)
    staff_emails = get_receipients(redcap)

    # Required Patient Fields
    pfields = ['rc_id', 'phone1','phone2','email1','email2', 'first_name', 'last_name']
    precords = {}

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
          site = patient['rc_id'].upper()         

          # The testing site visited by this patient is not configured 
          # to send email reminders. So continue to the next patient
          if site.startswith(tuple(rem_keys)) == False:
            continue
          if patient['email1'] == '':
            # ignore patients for whom we don't have email IDs
            if patient['email2'] == '':
              continue
            else:
              # Set the primary email and delete the secondary
              patient['email1'] = patient['email2']
              patient['email2'] = ''
              to_update.append(patient)
          
          if patient['email1'] in hash_email:
            hash_email[patient['email1']].append(patient['rc_id'])
          else:
            hash_email[patient['email1']] = [patient['rc_id']]
            hash_names[patient['email1']] = { 'first_name' : patient['first_name'],
                                              'last_name' : patient['last_name'] 
                                            }

          site_rcid[patient['rc_id'][:-5]].append(patient['rc_id'])
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
      fields = ['rc_id','visit_date','rapid1', 'rapid2', 'testing_reminder','dhiv', 'lstremndr_dt']
      for site, records in site_rcid.iteritems():
        log.debug("Site: %s, Requesting: %d records", site, len(records))
        patient_history.extend(redcap.project[site].export_records(records=records, fields=fields))

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
        for rc_id in val:
          try:
            
            if hist_map[rc_id]['visit_date'] == '':
              skip = True
              break
            print 'visit date exists'
            visit = datetime.strptime(hist_map[rc_id]['visit_date'],
                                      "%Y-%m-%d")
            if latest_record == None:
              latest_record = hist_map[rc_id]
            else:
              latest_date= datetime.strptime(latest_record['visit_date'],"%Y-%m-%d") 
              if latest_date < visit:
                print 'compare dates'
                print visit
                print latest_date
                latest_record = hist_map[rc_id]
          except KeyError:
            log.critical(traceback.format_exc())

        if skip == True:
          continue
        print 'latest record'
        print latest_record
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
                             'unsubscribe_url'  : settings['unsubscribe_url'] + '?email='+ key +"&rc_id=" + latest_record['rc_id'] + "&unsubscribe.submitted=Unsubscribe",
                             'phone'            : settings['phone'],
                             'email'            : key
                            }
          try:
            turbomail.send(turbomail.Message(
                          author="UCSD - Good to Go<" + settings["remind.email"] + ">",
                          organization=["UCSD - Good to Go"],
                          bcc=[key],
                          reply_to=settings["remind.email"],
                          subject="UCSD Early Test - Good to Go reminders",
                          rich = lookup.get_template('email/reminder.mako').render(**template_input),
                          headers =  {'list-unsubscribe': "<" + template_input['unsubscribe_url'] 
                                                               + ">,<mailto:" + settings["remind.email"] +">"},
                          plain = "this is a reminder email to complete early test at " + settings['ltw_url']))
            count = count + 1
            match = next(d for d in patient_history if d['rc_id'] == latest_record['rc_id'])
            print 'patient email date record '
            print match
            if match != '':
              match['lstremndr_dt'] = datetime.today().date().strftime('%Y/%m/%d')
              
          except:
            invalid_emails[latest_record['rc_id']] = key
            log.critical(traceback.format_exc())
            pass
        
      try:
        redcap.project[site].import_records(patient_history)
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
             'patient_count': len(hash_email.keys()),
             'emails_sent': count,
             'invalid_emails_count':invalid_emails_count
            }
      template = "<html><head></head><body>HELLO {{ value }} </body></html>" 
      send_email(template, {"value" : "World"}, "Test", "uni@ucsd.edu", ["fakhra.anwer@gmail.com"])
      try:
        text = lookup.get_template('email/stats.mako').render(**stats)
        turbomail.send(turbomail.Message(
                        author = "UCSD - Good to Go<" + settings["remind.email"] + ">",
                        organization = ["UCSD - Good to Go"],
                        to = staff_emails,
                        reply_to = settings["remind.email"],
                        subject = "Good to Go Email Reminders Statistics",
                        plain = text))
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
    if ['lstremndr_dt'] == datetime.today().date().strftime('%Y/%m/%d'):
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
   
def get_receipients(redcap):
  email_list = []
  records = redcap.project['Email'].export_records()
  for record in records:
    if record['et_mail_stats'] == '1':
      email_list.append(record['email'])
  return email_list

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
