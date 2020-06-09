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
import logging, json, operator
from avrc.redcross import exc, log, Session, models, config

ERR = -1
NO_ERR = 0  

class RCProject:
 
  def __init__(self, site_code, rcsettings):
    try:
      self.cap_url = rcsettings['cap_url']
      self.nat_fields= ['rc_id', 'visit_date', 'nat_expected', 'nat_result_date', 
                        'nat', 'dhiv', 'dhcv', 'dhbv', 'nat_sco', 'dhiv_sco', 'dhbv_sco', 'dhcv_sco', 'test_site', 'nat_test_complete', 'nat_results_complete', 'qc_review_complete']
      self.token = {}
      self.exp_date = rcsettings['exp_date']
      self.token['CTS'] = rcsettings['cap_key']['CTS']
      self.token['Email'] = rcsettings['cap_key']['Email']
      for site in site_code:
        try:
          self.token[site] =rcsettings['cap_key'][site]
        except KeyError:
          continue
      self.project = {}
      self.connect_project()
    except:
      raise
  
  def connect_project(self):
        try:
            if datetime.datetime.strptime(self.exp_date, "%Y-%m-%d").date() <= datetime.date.today():
                raise exc.RedCAPTokenExpired(exp_date)
            # There can be multiple project that have our data
            for site, tok in self.token.iteritems():
              print 'site'
              print site
              self.project[site] = Project(self.cap_url, tok, verify_ssl=True)
              log.info('Project connected to: %s data' % site)
        except:
            raise


  def generate_reports (self, request=None, ref_no=None, reports_start = 0, reports_end = 0):
  
    records = []
    #This records list should be filtered before display
    for site, proj in self.project.iteritems():
      records.extend(proj.export_records(fields=self.nat_fields, raw_or_label='raw'))
    
    reports_max = len(records)
    if reports_end == 0:
      reports_end = reports_max
    
    if request !=None:
      reports = self.filter_by_conditions(records, request, ref_no)

    return reports[reports_start:reports_end+1]

  def filter_by_conditions(self, records, request, reference_number=''):
    try:
      #NAT expected will only be set to records in the future after 2017/04 
      for record in records:
        try:
          if record['nat_expected'] == False and record['nat_result_date'] == "":
            records.remove(record)
        except KeyError as e:
            pass
        
      #Filter out site specific records and conditions
      results = []
      for record in records:
        for site in self.project.keys():
          if record['rc_id'].startswith(site):
            if 'no_filter' in request.GET or self.subfilter_options(record, request):
              if record['rc_id'].find(reference_number.upper()) != -1:
                results.append(record)
                break
    except:
      raise
    return results

  def get_location_label(self, reports):
    try:
      req_rcid = []
      #Create a chunk of rcids to request the server
      for report in reports:
        req_rcid.append(report['rc_id'])

      lfields = ['test_site', 'rc_id']
      loc_map = []
      
      for site, proj in self.project.iteritems():
        loc_map.extend(proj.export_records(records=req_rcid, fields=lfields, raw_or_label='label'))
      
      rcid_map = {}
      for element in loc_map:
        try:
          if element['test_site'] != "":
            # Some of the projects doesn't have a test_site
            # 15 character abbreviation for aesthetic reasons
            rcid_map[element['rc_id']] = element['test_site'][:13] + "."
        except KeyError as k:
          rcid_map[element['rc_id']] = ""
          continue
    
      for report in reports:
        try:
          report['test_site'] = rcid_map[report['rc_id']]
        except KeyError as k:
          continue
        
    except RuntimeError as e:
      #Not an important function
      #Ignore the exception
      print(e)
      pass
    
    return reports  

  def subfilter_options(self, record, request):
    filter_options = {'dhiv':'P', 'dhcv':'P', 'dhbv':'P', 'visit_date': ""}
    expected, satisfied = 0, 0
    for key, val in filter_options.iteritems():
      try:
        if key in request.GET:
          expected += 1
          if record[key] == val:
            satisfied += 1
      except KeyError:
        # No such filter options 
        # continue silently
        pass

    if expected == satisfied:
      return True

    return False

  def sorted_reports(self, reports):
    try:
        sorted_result = []
        cp_reports = copy.deepcopy(reports)
        #Get the line items with no result first
        for report in reports:
          if report['nat_result_date'] == "":
            sorted_result.append(report)
            cp_reports.remove(report)

        sorted_result = sorted(sorted_result, key=operator.itemgetter('visit_date'), reverse = True)

        #Get the line items with missing draw dates
        cp2_reports = copy.deepcopy(cp_reports)
        for report in cp_reports:
          if report['visit_date'] == "" :
            sorted_result.append(report)
            cp2_reports.remove(report) 
        
        cp2_reports = sorted(cp2_reports, key=operator.itemgetter('nat_result_date'), reverse = True)
        sorted_result.extend(cp2_reports)
        return sorted_result
    except RuntimeError as e:
      print(e)
      return reports
   
  def chunked_get_records(self, project, chunk_size=100):
    def chunks(l, n):
      '''Yield n-succesive sized chunks from list l '''
      for i in xrange(0, len(l), 1):
        yield l[i: i+n]

    record_list = project.export_records(fields=project.def_field) 
    records = [r[project.def_field] for r in record_list]
    print("Total Records" % len(records))
    try:
      response = []
      for record_chunk in chunks(records, chunk_size):
        chunked_response = project.export_records(records= record_chunk)
        response.extend(chunked_response)
    except RedcapError:
      msg = "Chunked Export Failed for chunk size=(:d)".format(chunk_size)
      raise ValueError(msg)
    else:
      return response   
            
  def get_records(self, records, fields=None):
      ''' Utility to get the individual record
        from the redcap db
          
          Parameters: 
              'redcap'    - RedCAP project handles.
              'rc_id_list' - dict with (rc_id, result) as (key, val).
          
          Return:
              'response' - return value from export_records
      '''

      try:
          if fields == None:
            fields = self.nat_fields 
          responses = []
          for site in self.project.keys():
            for rc_id, value in records.iteritems():
              site_set= []
              if site == rc_id[:-5]:
                site_set.append(rc_id)
            
            if len(site_set) != 0:
              responses.extend(self.project[site].export_records(records=site_set, fields=fields))
    
          log.info("Requested rows: %d Retrieved rows:%d" % (len(records), len(responses)))
      except:
        raise
      return responses

  def put_records(self, records):
    
    try:
      error = {}
      # Create sublist to update different projects
      spare_records = copy.deepcopy(records)
      expected = len(records)
      for site, proj in self.project.iteritems():
        site_records = []
        for record in records:
            if record['rc_id'][:-5] == site:
              #Take only the required fields
              site_records.append(record)
        
        response = proj.import_records(site_records, date_format='YMD')
        print(response)
        if response['count'] != len(site_records):
          log.critical("Response not matched for site:%s", site)
          error[site] = {'expected': len(site_records), 'updated': response['count'], 'values':site_records}
         
    except:
      raise
    
    return error  
