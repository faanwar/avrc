import os
import platform
import re
import json
import traceback
import gnupg
from avrc.redcross import exc, log, models, Session 
import datetime
from redcapi import RCProject
import csv

def get_redcap_results(settings):
    sites = settings.get('site.codes').split()
    rcs = json.loads(open(settings['redcap_json'],'r').read())

    redcap = RCProject(sites, rcs)

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

    results.append(result)