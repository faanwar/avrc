import argparse
import datetime
import os
import shutil
import tempfile
import traceback
import json
import turbomail

from avrc.redcross import log, lookup, Session, models, parser, config, RCProject, sync_redcap

cli = argparse.ArgumentParser(description='Proceses an encrypted Red Cross File')
cli.add_argument(
    '-c', '--config',
    dest='settings',
    type=config.from_file,
    metavar='FILE',
    help='Configuration File')
cli.add_argument(
    '--dry',
    action='store_true',
    help='Disables modification of the database and filesystem. Will still email')



def main():
    args = cli.parse_args()
    settings = args.settings

    days_till_expiration = int(settings['days.tillexpiration'])
    days_till_notify = int(settings['days.tillnotify'])

    try:	
        results = sync_redcap.get_cts_results(settings)
        if not args.dry:
            Session.add_all(results)
            Session.commit()

        else:
            log.info('Dry run, not commiting changes')

        
        sync_site_codes = settings.get('site.codes').split()
        rcs = json.loads(open(settings['redcap_json'], 'r').read())
        redcap = RCProject(sync_site_codes, rcs)
        # Refresh results
        for site_code in sync_site_codes:
            print 'site code'
            print site_code
            for type_ in models.TYPES:
                #notify = settings.get('notify.%s.%s' % (site_code.lower(), type_.lower()), '').split()
                notify = []
                print type_
                pnt = list(r for r in results if r.check(type_) is True and r.site_code == site_code)
                neg = [r for r in results if r.check(type_) is False and r.site_code == site_code]
                odd = [r for r in results if r.check(type_) is None and r.site_code == site_code]

                if not (pnt):
                    continue
                'clear'
                if type_ == 'dhiv':
                    notify = get_receipients(redcap, 'hiv_pos')
                    t_type = 'HIV'
                elif type_ == 'dhcv':
                    notify = get_receipients(redcap, 'hcv_pos')
                    t_type = 'HCV'
                elif type_ == 'dhbv':
                    notify = get_receipients(redcap, 'hbv_pos')
                    t_type = 'HBV'

                print notify
                if not notify:
                    continue

                turbomail.send(turbomail.Message(
                    to=notify,
                    subject='New %s+ NAT' % t_type,
                    plain=lookup.get_template('email/parse.mako').render(**{
                        'timestamp': datetime.datetime.now(),
                        'type_': t_type,
                        'site_code': site_code,
                        'pnt': pnt,
                        'neg': neg,
                        'odd': odd})))

                log.info('Notified %s mailing lists of results for "%s"' % (site_code, type_))

        
        for code in sync_site_codes:
            results_count = 0
            shouldNotify = False

            # Get number of site specific results in this upload
            for r in results:
                if r.site_code == code.upper():
                    results_count += 1

            # Get list of results with missing draw dates
            missing_draw = find_missing_draw(days_till_expiration, code)
            missing_draw_count = len(missing_draw)

            # Get list of draw dates with missing Red Cross results that are more than 7 days old
            missing_results = find_missing_results(days_till_notify, days_till_expiration, redcap, code)
            missing_results_count = len(missing_results)
            
            # Notify recipients if there is anything to notify about
            if results_count > 0 or missing_results_count > 0 or missing_draw_count > 0:
                shouldNotify = True

            if shouldNotify:
                notify = settings.get('notify.%s.sync' % code.lower()).split()
                
                # Notify appropriate people about missing draw dates and Red Cross results
                turbomail.send(turbomail.Message(
                    to=notify,
                    subject='[The Early Test]: Red Cross Synchronize Report (%s)' % code,
                    plain=lookup.get_template('email/sync.mako').render(**{
                        'timestamp':      datetime.datetime.now(),
                        'results_count': results_count,
                        'missing_draw_count':  missing_draw_count,
                        'missing_draw':      missing_draw,
                        'missing_results_count': missing_results_count,
                        'missing_results': missing_results,
                        'days_till_notify': days_till_notify,
                        'code': code})))

                log.info('Notified mailing lists of %s for missing draw dates' % (code))
                log.info('Notified mailing lists of %s diagnostic for missing Red Cross results' % (code))

    except:
        # If an unexpected error occurs, let the developers know
        turbomail.send(turbomail.Message(
            to=settings['notify.error'].split(),
            subject='[The Early Test]: Parser failed execution',
            plain=traceback.format_exc()))
        raise

# Returns a list of missing draw that are less than 180 days old
def find_missing_draw(days_till_expiration, code):
    current_time = datetime.date.today()
    results_expiration = current_time - datetime.timedelta(days=days_till_expiration)
    missing_draw = Session.query(models.Result).filter(models.Result.site_code==code).filter(models.Result.draw_date==None).filter(models.Result.test_date > results_expiration).all()
    return missing_draw

# Returns a list of missing results that are 7 days old but not greater than 180 days old
def find_missing_results(days_till_notify, days_till_expiration, redcap, code):
    # Missing results can be directly obtained from redcap
    try:
      missing_results = []
      current_time = datetime.date.today()
      results_notification = current_time - datetime.timedelta(days=days_till_notify)
      results_expiration = current_time - datetime.timedelta(days=days_till_expiration)
      all_records = redcap.project[code].export_records(fields=redcap.nat_fields)

      for record in all_records:
        if record['nat_expected'] == True and record['nat_result_date'] == '':
          if record['visit_date'] > results_notification and record['visit_date'] < results_expiration:
            missing_results.append(record)
    except KeyError:
      pass

    return missing_results

def get_receipients(redcap, result_type):
    email_list = []
    records = redcap.project['Email'].export_records()
    for record in records:
        if record[result_type] == '1':
            email_list.append(record['email'])
    return email_list

