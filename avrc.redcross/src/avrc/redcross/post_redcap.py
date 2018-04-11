# This software is Copyright(c) 2017,
# The Regents of the University of California
#
#
# Core Developers
#    Ajay Mohan(ajmohan@ucsd.edu)
#
""" 
* This script updates the RedCAP projects with the results received
from RedCross. 

* This removes the dependency on a separate sqlite earlytest db. 

* All the transactions will now be managed directly with RedCAP db.

* Expected usage is to have an incron trigger this command when the Red Cross sends a file via FTP
"""
 
import argparse, os, copy, turbomail, tempfile, datetime
import traceback, logging
from avrc.redcross import exc, log, Session, models, parser, config, RCProject

def update_redcap(settings, fname):
    rcs = json.loads(open(settings['redcap_json'], 'r').read())
    redcap = RCProject(settings.get('site.codes').split(), rcs)
    response, records = write_results(redcap, settings, fname)
    return redcap, response


def write_results(redcap, settings, fname):
    ''' Utility to write the results in to 
        redcap db

        Parameters: 
            'project' - RedCAP project handle from connect_project.
            'results' - dict with (rc_id, result) as (key, val).
        
        Return:
            'response' - return value from put_records RCProject class
            'records'  - the total records that were updated in the db
    '''

    try:
        results = parse_results(fname, settings)
        print(type(results))
        
        # The test date is the date when RedCross sends us the result, 
        # which is the file copy time
        test_date = datetime.datetime.fromtimestamp(parser.get_test_date(fname)).strftime("%Y-%m-%d")
        
        #spare_results = copy.deepcopy(results)
        
        # records is a list of dictionaries
        records = redcap.get_records(results)

        for record in records:
          print(record)
          # Update the nat result record by record 
          nat_result = results[record['rc_id']]
          for key,values in nat_result.iteritems():
              record[key] = values
          record['nat_result_date'] = test_date
          # remove the updated result from the result dictionary
          del results[str(record['rc_id'])]


        if len(results) is not 0:
            # Results not being empty indicates the some RCIDS 
            # are not in RedCAP yet
            new_records = results
            for rc_id, nat_result in new_records.iteritems():
                new_record = {}
                new_record['rc_id'] = rc_id
                new_record['nat'] = 'Y'
                new_record['nat_result_date'] = test_date
                for key,val in nat_result.iteritems():
                    new_record[key] = val
                records.append(new_record)
        else:
            print("No new records") 
        response = redcap.put_records(records)
    except:
      raise 
  
    return response, records


def parse_results(src_file, settings):
    log.info('Called on %s' % src_file)
   
    #A temporary file to store the results
    with tempfile.NamedTemporaryFile('rw') as fp:
        parser.decrypt(src_file, fp.name,
                passphrase=settings['gpg.passphrase'],
                home=settings['gpg.home'], 
                binary=settings['gpg.binary']) 
        results = parser.parse(fp.name, True)
    return results

