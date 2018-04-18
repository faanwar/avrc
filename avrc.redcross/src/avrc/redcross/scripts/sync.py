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

from avrc.redcross import RCProject, models, Session, log, config, lookup
from datetime import datetime as dt
import argparse
import transaction
import turbomail
import json
import sqlite3
import traceback
import datetime

cli = argparse.ArgumentParser(description='Sync the SQLITE db results with redcap changes')

cli.add_argument(
    '-c', '--config',
    dest='settings',
    type=config.from_file,
    metavar='FILE',
    help='Configuration File')

def time_in_range(x, start= datetime.time(8,0,0), end = datetime.time(8, 59,0)):
    """Return true if x is in the range [start, end]"""
    """ This API is required to ensure that we send a report only once a day between 8:00am - 8:59am"""
    if start <= end:
        return start <= x <= end
    else:
        return start <= x or x <= end

def bucketize_results():
  """ Returns a dictonary of buckets which has site_codes as keys
      and list of results as values"""

  buckets = {}
  try:    
    all_results = Session.query(models.Result) 
   
    site_codes = []
    for result in all_results:
      try:
        if result.site_code not in site_codes:
          site_codes.append(result.site_code)
          buckets[result.site_code] = []
      
        buckets[result.site_code].append(str(result.site_code) + str(result.reference_number))
      except:
        pass    
  except Exception as e:
    log.critical(traceback.format_exc())
 
  return buckets

def sync_sql_result(buckets, settings):
  """ 
      Parameters: 
            
            buckets: Dict of site codes and list of Results for that site as key, value pairs
            
            settings: A dictionary of settings specified in the configuration file            
      Returns None
  """
  try:
    log.info("Synchronization Routine Started")
    #only two attributes could have been updated Draw Date or Location
    #Result should not be modified in the RedCAP directly
   
    rcs = json.loads(open(settings['redcap_json'], 'r').read())
    
    # Days after which results become invalid
    days_till_expiration = int(settings['days.tillexpiration'])

    # Days after which results can be published to patients
    days_till_notify = int(settings['days.tillnotify'])

    # Days after which tester should definitely act ASAP on CRF's or redcap entries
    days_till_urgent = int(settings['days.tillurgent'])

  
    redcap = RCProject(buckets.keys(), rcs)
    ctsrecords = []
    for key, value in buckets.iteritems():
  
      # These malformed draw dates need to be handled offline. This script will only be
      # reporting such entries
      malformed_draw = []

      # Unmindful check. This line is mostly a deadcode, I guess.
      if key not in redcap.project.keys():
        continue
      
      #fields = ['visit_date','test_site']
    
      # we pass the 'label' flag to get the location value as string instead numeric values
      records = redcap.project[key].export_records(records=value,fields=redcap.nat_fields,raw_or_label='label') 
      
      ctsrecord = redcap.project['CTS'].export_records(records=value, fields='rec_status')
      for each in ctsrecord:
        new_ctsrecord = {}
        new_ctsrecord['rc_id'] = each['rc_id']
        new_ctsrecord['rec_status'] = 1
      ctsrecords.append(new_ctsrecord)

      # RCIDs for which we have new results will be in push records
      push_records = []
      for record in records:
            
        sql_row = Session.query(models.Result)\
                    .filter(models.Result.site_code == key)\
                    .filter(models.Result.reference_number == record['rc_id'][-5:]).first()
        
           
        # Visit/Draw date update in SQL DB
        if 'visit_date' in record.keys() and record['visit_date'] != '':
          visit_date =  dt.strptime(record['visit_date'], "%Y-%m-%d").date() 

          if sql_row.draw_date != visit_date:
            if sql_row.test_date >= visit_date:
              sql_row.draw_date = visit_date

              min_visit_date = sql_row.test_date - datetime.timedelta(days=int(settings['result_buffer']))
              if visit_date < min_visit_date:
                malformed_draw.append(record['rc_id']) 

            # The malformed draw dates are the ones that don't fall in to the 
            # accepted window for results. Just report them, nothin more.
            else:
              malformed_draw.append(record['rc_id'])
   
        # Location update in SQL DB
        if 'test_site' in record.keys() and record['test_site'] != '':
          if sql_row.location != record['test_site']:
            sql_row.location = record['test_site'] 
      
        # Keep track for bulk update in RedCAP later
        if 'nat_result_date' in record.keys():
          if record['nat_result_date'] == '':
            push_records.append(update_result_redcap(record, sql_row))
          else:
            if 'nat_test_complete' in record.keys() and \
                record['nat_test_complete'] == "Incomplete":
            
              new_record = {}
              new_record['rc_id'] = record['rc_id']
              new_record['nat_test_complete'] = 2
              push_records.append(new_record)
             
        Session.commit()

      # Make the bulk update for every 'key' and 'site'
      value = redcap.project[key].import_records(push_records)
      redcap.project['CTS'].import_records(ctsrecords)
       
      # The following lines form the sophisticated email system ;-P. Well we again 
      # ask the human to help.
 
      malformed_draw_count = len(malformed_draw)
      # Get list of results with missing draw dates
      missing_draw, warn_draw, critical_draw  = find_missing_draw(days_till_expiration, days_till_urgent, key)
      missing_draw_count = len(missing_draw)
      warn_draw_count = len(warn_draw)
      critical_draw_count = len(critical_draw)
      
      weekday = datetime.date.today().weekday() 
      
      
      if warn_draw_count !=0 and time_in_range(datetime.datetime.now().time()) and weekday == 5:
        #Special notifications when draw dates are missing for days_till_urgent
        # This notification is sent on Fridays(5)
        report_date = warn_draw
        report_date_count = warn_draw_count
        level = 1
        notify = settings.get('notify.%s.action' % key.lower()).split()
        turbomail.send(turbomail.Message(
                  to=notify,
                  subject='[RedCAP Sync Update]: Prolonged Missing RedCAP Entries for (%s)' % key,
                  plain=lookup.get_template('email/date.mako').render(**{
                      'timestamp':      datetime.datetime.now(),
                      'report_date': report_date,
                      'report_date_count':  report_date_count,
                      'level':  level,
                      'days_till_urgent': days_till_urgent,
                      'code': key})))


      if critical_draw_count !=0:
        # Very critical draw date events emailed everyday
        # Between 8-9am
        
        time_now = datetime.datetime.now().time()
        if time_in_range(time_now):
          
          log.info("Some of the draw dates are missing for over %d days" % (int(days_till_urgent) + 2))
          report_date = critical_draw
          report_date_count = critical_draw_count
          level = 2
          notify = settings.get('notify.%s.action' % key.lower()).split()
          turbomail.send(turbomail.Message(
                    to=notify,
                    subject='[RedCAP Sync]: Action Required in RedCAP Entries for (%s)!' % key,
                    plain=lookup.get_template('email/date.mako').render(**{
                        'timestamp':      datetime.datetime.now(),
                        'report_date': report_date,
                        'report_date_count':  report_date_count,
                        'level':  level,
                        'days_till_urgent': days_till_urgent,
                        'code': key})))


      # Get list of draw dates with missing Red Cross results that are more than 7 days old
      missing_results = find_missing_results(days_till_notify, days_till_expiration, redcap, key)
      missing_results_count = len(missing_results)
     
      shouldNotify = False 
      # Notify recipients if there is anything to notify about only if its a Monday
      if missing_results_count > 0 or missing_draw_count > 0 and datetime.date.today().weekday() == 1:
          shouldNotify = True
      
      if shouldNotify and time_in_range(datetime.datetime.now().time()):
          notify = settings.get('notify.%s.action' % key.lower()).split()
                
          # Notify appropriate people if notify is set to true
          turbomail.send(turbomail.Message(
              to=notify,
              subject='[RedCAP Sync]: Synchronization Status Check (%s)' % key,
              plain=lookup.get_template('email/rcap.mako').render(**{
                  'timestamp':      datetime.datetime.now(),
                  'results_count': 0,
                  'missing_draw_count':  missing_draw_count,
                  'missing_draw':      missing_draw,
                  'missing_results_count': missing_results_count,
                  'missing_results': missing_results,
                  'days_till_notify': days_till_notify,
                  'days_till_urgent': days_till_urgent,
                  'code': key,
                  'malformed_draw_count':malformed_draw_count,
                  'malformed_draw': malformed_draw})))

    
  except: 
    turbomail.send(turbomail.Message(
        to=settings['notify.error'].split(),
        subject='[The Early Test]:Exception in matching visit dates!',
        plain=traceback.format_exc()))
  
# Returns a list of missing draw that are less than 180 days old
def find_missing_draw(days_till_expiration, days_till_urgent, code):
    current_time = datetime.date.today()
    results_expiration = current_time - datetime.timedelta(days=days_till_expiration)
    
    warn_missing = current_time -datetime.timedelta(days=days_till_urgent)
    critically_missing = warn_missing - datetime.timedelta(days=2)
    
    missing_draw = Session.query(models.Result).filter(models.Result.site_code==code).filter(models.Result.draw_date==None).filter(models.Result.test_date > warn_missing).all()
    
    warn_missing_draw = Session.query(models.Result).filter(models.Result.site_code==code).filter(models.Result.draw_date==None).filter(models.Result.test_date > critically_missing).filter(models.Result.test_date <= warn_missing).all()

    critically_missing_draw = Session.query(models.Result).filter(models.Result.site_code==code).filter(models.Result.draw_date==None).filter(models.Result.test_date <= critically_missing).filter(models.Result.test_date > results_expiration).all()

    return missing_draw, warn_missing_draw, critically_missing_draw

# Returns a list of missing results that are 7 days old but not greater than 180 days old
def find_missing_results(days_till_notify, days_till_expiration, redcap, code):
    # Missing results can be directly obtained from redcap
    try:
      missing_results = []

      # Adjust timings to relavant intervals
      current_time = datetime.date.today()
      results_notification = current_time - datetime.timedelta(days=days_till_notify)
      results_expiration = current_time - datetime.timedelta(days=days_till_expiration)

      # Fetch all records from redcap
      all_records = redcap.project[code].export_records(fields=redcap.nat_fields)
      for record in all_records:
        if record['nat_expected'] == True and record['nat_result_date'] == '':
          if record['visit_date'] < results_notification and record['visit_date'] > results_expiration:
              missing_results.append(record)
    except KeyError:
      pass

    return missing_results

def update_result_redcap(record, sql_row):
  try:
    for attr_name in ['nat_result_date', 'nat',\
                       'dhiv', 'dhcv', 'dhbv', 'nat_test_complete', 'nat_sco', 'dhiv_sco', 'dhcv_sco' , 'dhbv_sco']:
    
      if attr_name in record.keys():
        # This field name do not match in redcap and sql hence this hacky solution
        if attr_name == 'nat_result_date':
          record[attr_name] = sql_row.test_date.strftime("%Y-%m-%d")
        elif attr_name == 'nat_test_complete':
          # 0. Incomplet 1. Verified 2. Complete
          record[attr_name] = 2
        else:
          record[attr_name] = getattr(sql_row, attr_name)
    
    # Removing the location key from dict, as we don't need to update it
    # Return none if not present
    record.pop('test_site', None)
    return record
  except Exception as e:
    raise

def main():
  try:
    args = cli.parse_args()
    settings = args.settings

    buckets = bucketize_results()
    sync_sql_result(buckets, settings)
     
  except Exception as e:
    log.critical(e)
    turbomail.send(turbomail.Message(
        to=settings['notify.error'].split(),
        subject='[The Early Test]: RedCAP - SQLite DB Synchronization Error!',
        plain=traceback.format_exc()))
  
