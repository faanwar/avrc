# Core Developers
#    Ajay Mohan(ajmohan@ucsd.edu)
#
from redcap import Project
import argparse 
import os
import copy
import turbomail
import tempfile
import datetime
import traceback
import logging
from avrc.redcross import exc, log, Session, models, parser, config

cli = argparse.ArgumentParser(description="Process RedCross encrypted file")

cli.add_argument(
    '-c', '--config',
	metavar='FILE',
	type=config.from_file,
	dest='settings', help='Configuration File')

def connect_project(settings):
    url = settings['cap_url']
    key = settings['cap_key']
    exp_date = settings['exp_date']

    try:
        if datetime.datetime.strptime(exp_date, "%Y-%m-%d").date() <= datetime.date.today():
            raise exc.RedCAPTokenExpired(exp_date)
        project = Project(url, key, verify_ssl=True)
        log.info('Project connected: %s' % project)
    except:
        log.critical('Exception on RedCap Project connect')	
        turbomail.send(turbomail.Message(
            to=settings['notify.error'].split(),
            subject='[The Early Test]: RedCap Connection failure',
            plain=traceback.format_exc()))
        raise
    return project

def get_record(project, rc_id_list):
    ''' Utility to get the individual record
	    from the redcap db
        
        Parameters: 
            'project'    - RedCAP project handle received from connect_project.
            'rc_id_list' - dict with (rc_id, result) as (key, val).
        
        Return:
            'response' - return value from export_records
    '''

    try:
        records = rc_id_list
        fields = ['nat', 'dhiv', 'dhbv', 'dhcv', 'nat_test_complete']
        response = project.export_records(records=records, fields=fields, format='json')
        log.info("Requested rows: %d Retrieved rows:%d" % (len(records), len(response)))
    except:
	    raise
    return response

def write_results(project, filename, settings):
    ''' Utility to write the results in to 
        redcap db

        Parameters: 
            'project' - RedCAP project handle received from connect_project.
            'results' - dict with (rc_id, result) as (key, val).
        
        Return:
            'response' - return value from import_records
    '''

    try:
        results = parse_results(filename, settings)
        #test_date = get_test_date(filename)
        spare_results = copy.deepcopy(results)
        rc_id_list = []
        for rc_id in results:
            rc_id_list.append(rc_id)
        
        print("RC_ID results:",rc_id_list)
        # records is a list of dictionaries
        records = get_record(project, rc_id_list)
        
        for record in records:
            # Update the nat result record by record 
            nat_result = results[record['rc_id']]
            for key,values in nat_result.iteritems():
                record[key] = values
        # remove the updated result from the result dictionary
	    del results[str(record['rc_id'])]

        if len(results) is not 0:
            # The following are the rcids not in the table
            # Create new records for them
            print("Length of new records")
            print(len(results))
            for rc_id,nat_result in results.iteritems():
                new_record = {}
                new_record['rc_id'] = rc_id
                new_record['nat'] = 'Y'
                for key,val in nat_result.iteritems():
                    new_record[key] = val
                records.append(new_record)
        
        response = project.import_records(records)
    except:
	    raise
    return response

def parse_results(src_file, settings):
    log.info('Called on %s' % src_file)
   
    #A temporary file to store the results
    with tempfile.NamedTemporaryFile('rw') as fp:
        parser.decrypt(src_file, fp.name,
                passphrase=settings['gpg.passphrase'],
                home=settings['gpg.home'], 
                binary=settings['gpg.binary']) 
        results = parser.parse(fp.name)
    return results
	
def main():
    args = cli.parse_args()
    settings = args.settings
    if settings == None:
        cli.print_help()
        return
    print(settings)
    project = connect_project(settings)
    response = write_results(project, "UCSD_Results.exp", settings)
    print(response)

main()
	
