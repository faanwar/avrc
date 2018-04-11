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
#   Zachary Smith (z4smith@ucsd.edu)
#
# Significant contributions from:
#   David Mote (davidmote [at] gmail [dot] com)
#   Jennifer Rodriguez-Mueller (almostlikethat [at] gmail [dot] com)
#   Drew Allen (asallen@ucsd.edu)
#   Andrew Dang (a7dang [at] gmail [dot] com)
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

"""
Updates Red Cross test result database from a specified encrypted result file

Expected usage is to have incron trigger this command when the Red Cross
sends a file via FTP.
"""

import argparse
import datetime
import os
import shutil
import tempfile
import traceback
import json
import turbomail

from avrc.redcross import log, lookup, Session, models, parser, config, RCProject


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
cli.add_argument(
    'srcfile',
    metavar='SRCFILE',
    help='The file to parse')


def main():
    args = cli.parse_args()
    settings = args.settings

    days_till_expiration = int(settings['days.tillexpiration'])
    days_till_notify = int(settings['days.tillnotify'])

    try:
        log.info('Called on %s' % args.srcfile)		
        results, duplicates = parser.parse(args.srcfile, settings)

        if not args.dry:
          
            if duplicates:
                raise Exception('\n'.join(
                    ['Already exists: %s%s' % (r.site_code, r.reference_number)
                    for r in duplicates]))

            # Archive processed file
            shutil.move(args.srcfile, settings['dir.raw'])
            log.info('Moved encrypted file to %s' % settings['dir.raw'])
	
      
            # Commit all changes now that we've successfully processed the file
            map(lambda r: setattr(r, 'file', os.path.basename(args.srcfile)), results)
            Session.add_all(results)
            Session.commit()

        else:
            log.info('Dry run, not commiting changes')

        
        sync_site_codes = settings.get('site.codes').split()
        rcs = json.loads(open(settings['redcap_json'], 'r').read())
        redcap = RCProject(sync_site_codes, rcs)
        # Refresh results
        for site_code in sync_site_codes:

            for type_ in models.TYPES:
                notify = settings.get('notify.%s.%s' % (site_code.lower(), type_.lower()), '').split()

                if not notify:
                    continue

                pnt = [r for r in results if r.check(type_) is True and r.site_code == site_code]
                neg = [r for r in results if r.check(type_) is False and r.site_code == site_code]
                odd = [r for r in results if r.check(type_) is None and r.site_code == site_code]

                if not (pnt or odd):
                    continue

                turbomail.send(turbomail.Message(
                    to=notify,
                    subject='[The Early Test]: New Records Notification (%s)' % type_,
                    plain=lookup.get_template('email/parse.mako').render(**{
                        'timestamp': datetime.datetime.now(),
                        'type_': type_,
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

