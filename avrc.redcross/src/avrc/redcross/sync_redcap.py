import os
import platform
import re
import json
import traceback
from avrc.redcross import exc, log, models, Session 
import datetime
from redcapi import RCProject
import csv


def get_cts_results(settings):
    sites = settings.get('site.codes').split()
    rcs = json.loads(open(settings['redcap_json'],'r').read())

    redcap = RCProject(sites, rcs)

    results = get_results(redcap)
    
    for result in results:
        # Syncing draw dates
        rc_id = str(result.site_code) + str(result.reference_number)
        draw = redcap.project[result.site_code].export_records([rc_id], fields=['visit_date', 'test_site'], raw_or_label="label")	
	    
        # Ignore if this information is not available in the redcap db
        try:
            if draw[0]['visit_date'] != '':     
                draw_date = datetime.datetime.strptime(draw[0]['visit_date'], "%Y-%m-%d").date()   
                result.draw_date = draw_date
        except:
		    pass
	      
        try:
            result.location = draw[0]['test_site']
        except:
            pass	

    return results

def get_results(redcap):

    def clean(s):
        """ Helper method to sanitize the string """
        return s.strip() or None

    results = []
    try:
        all_records = redcap.project['CTS'].export_records(fields=['rc_id', 'nat_results_complete'])       
        filtered_records = (x['rc_id'] for x in all_records if x['nat_results_complete'] == '2')   

        records = redcap.project['CTS'].export_records(records=filtered_records)

        for record in records:   
            print 'record'
            print record        
            rcid= record['rc_id']
            result = models.Result(
                site_code=rcid[:4],
                reference_number=rcid[-5:],
                nat=clean(record['nat']),
                nat_sco=clean(record['nat_sco']),
                dhiv=clean(record['dhiv']),
                dhiv_sco=clean(record['dhiv_sco']),
                dhcv=clean(record['dhcv']),
                dhcv_sco=clean(record['dhcv_sco']),
                dhbv=clean(record['dhbv']),
                dhbv_sco=clean(record['dhbv_sco']))
            results.append(result)
    except:
        pass
    return results