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

from aeh.earlytest.models import RootFactory
from pyramid.security import has_permission

from avrc.redcross import models
from aeh.earlytest import Session
from aeh.earlytest.views import *
from aeh.earlytest import models
from sqlalchemy import or_, and_, asc, desc
import transaction
from pyramid.response import Response, FileResponse, FileIter
from tempfile import NamedTemporaryFile
import os.path, math, csv, operator, datetime

class ReportViews:
    def __init__ (self, request):
        root = RootFactory(request)
        self.admins  = bool(has_permission('admins', root, request))
        self.avrc    = self.admins or bool(has_permission('avrc', root, request))
        self.oakland = self.admins or bool(has_permission('oakland', root, request))
        self.emory   = self.admins or bool(has_permission('emory', root, request))
        self.single_access = not self.admins and (self.avrc != self.oakland) and (self.avrc != self.emory) and (self.oakland != self.emory)

class ReportSite:
  def __init__(self, permissions):
    if permissions == 'admins':
      self.name = 'AVRC, Oakland, & Emory'
      self.codes = ['76C','76GH', '76FJ']
    elif permissions == 'avrc':
      self.name = 'AVRC'
      self.codes = ['76C']
    elif permissions == 'oakland':
      self.name = 'Oakland'
      self.codes = ['76GH']
    elif permissions == 'emory':
      self.name = 'Emory'
      self.codes = ['76FJ']
    else:
      self.name = 'Unknown Permissions'
      self.codes = []

def generate_reference_number (request):
  prev_ref_no = ''
  if 'reference_number' in request.GET and request.GET['reference_number'] != '':
    prev_ref_no = request.GET['reference_number']
  return str(prev_ref_no)

def generate_conditions (request, site_codes, reference_number=''):
  conditions = []
  all_conditions = []

  if 'no_filter' not in request.GET:
    if 'dhiv' in request.GET:
      conditions.append(models.Result.dhiv == 'P')
    if 'dhcv' in request.GET:
      conditions.append(models.Result.dhcv == 'P')
    if 'dhbv' in request.GET:
      conditions.append(models.Result.dhbv == 'P')
    if 'visit_date' in request.GET:
      conditions.append(models.Result.draw_date == None)
    condition_pre = and_(*conditions)
    all_conditions.append(condition_pre)

  all_conditions.append(models.Result.site_code.in_(site_codes))
  if reference_number != '':
      all_conditions.append(models.Result.reference_number.contains(reference_number))
  conditions = and_(*all_conditions)

  return conditions

def get_reports_max (conditions):
  session = Session()
  return int(session.query(models.Result).filter(conditions).count())

def generate_reports (conditions, reports_start = 0, reports_end = 0):
  session = Session()
  reports_max = int(session.query(models.Result).filter(conditions).count())
  if reports_end == 0:
    reports_end = reports_max

  return session.query(models.Result).filter(conditions).order_by(desc(models.Result.test_date)).slice(reports_start, reports_end)

def generate_slice_values (current_page, items_per_page):
  # 'pages' counts from 1 for users' sake, so we need to convert to an index
  start = (current_page - 1) * items_per_page
  end   = start + items_per_page - 1
  return \
  {
    'start': start,
    'end': end
  }

def process_csv (request, conditions):
  #
  # query all of the reports, store in a temporary CSV file and serve
  #
  reports = generate_reports(conditions) # report all in search query 
       
 

  f = NamedTemporaryFile('w+b', prefix='CSV_Export_1', suffix='.csv', delete=True)
  fcsv = csv.writer(f)

  fcsv.writerow(['RCID', 'Draw Date', 'Result Date', 'NAT', 'DHIV', 'DHCV', 'DHBV', 'Location'])

  for report in reports:
    fcsv.writerow([str(report.site_code)+str(report.reference_number), report.draw_date, report.test_date, report.nat, report.dhiv, report.dhcv, report.dhbv, report.location])

  f.seek(0)

  response = request.response
  response.content_type = 'application/csv'
  response.content_disposition='attachment; filename=%s' % 'export.csv'
  response.app_iter = FileIter(f)
  return response

def process_date_update(request, site_codes):
  # This method receives the GET request for draw date update
  # and updates the new date in the DB
  # FIX: Date validations should not be greater than 
 
  #redcap = RCProject(site_codes, rcs)
  max_date = datetime.date.today()
  min_date = max_date - datetime.timedelta(days=365)
   
  new_date_raw = request.GET['new_date_raw']
  print new_date_raw
  new_date = datetime.datetime.strptime(new_date_raw, "%Y-%m-%d").date()
  print new_date
  ref_num = request.GET['ref_num']
  site_code = request.GET['site']
  # retrieve the record from the db
	
  if min_date <= new_date and new_date <= max_date:
  	session = Session()
	record = session.query(models.Result).\
			filter(models.Result.site_code == site_code).\
			filter(models.Result.reference_number == ref_num).first()

	if record:
		record.draw_date = new_date
        	transaction.commit()
  return response 

class ReportPagination:
  def __init__(self, request, conditions, reports_per_page=50):
    """  
	ReportPageInfo: holds information about reports view
    """	
    
    self.reports_per_page = reports_per_page
    self.reports_max = get_reports_max(conditions)
    self.max = 1 + int(math.ceil(self.reports_max / self.reports_per_page))

    self.current = 1
    if 'page' in request.GET:
      self.current = int(request.GET['page'])
    if self.current < 1:
      self.current = 1
    elif self.current > self.max:
      self.current = self.max

    self.start = self.current - 4
    if self.start < 1:
      self.start = 1

    self.end = self.start + 9
    if self.end > self.max:
      self.end = self.max

class SortedPage:
  def __init__(self, request):
    self.item = 'test_date'
    if 'sort_by_item' in request.GET:
      self.item = request.GET['sort_by_item']
    self.dir = 'down'
    if 'sort_by_dir' in request.GET:
      self.dir = request.GET['sort_by_dir']

    self.reverse = False
    if self.dir == 'up':
      self.reverse = True

def process(request, login_status, csv_export=False, update_date=False, default_view={}):
  # generate site code/name
  site = ReportSite(login_status)
  

  # generate conditions list for filtering, update search terms
  prev_ref_no = generate_reference_number(request)
  conditions = generate_conditions(request, site.codes, prev_ref_no)
  
  # handle page-side requests the same as URL dispatches
  if csv_export== True or ('action' in request.GET and request.GET['action'] == 'export'):
    return process_csv(request, conditions)

  # update the specific date in the db
  if 'action' in request.GET and request.GET['action'] == 'update_date':
    return process_date_update(request, conditions)
 
  # generate and validate pagination info based on conditions
  p = ReportPagination(request, conditions)

  # query a slice of the reports
  s = generate_slice_values(p.current, p.reports_per_page)
  reports = generate_reports(conditions, s['start'], s['end'])

  # generate a sort-by
  sort = SortedPage(request)

 
  # set page start/end/max for search results
  ret = {
    'login_status': login_status,
    'site_name':    site.name,
    'prev_ref_no':  prev_ref_no,
    'max_pages':    p.max,
    'page':         p.current,
    'page_start':   p.start,
    'page_end':     p.end,
    'reports':      reports,
    'sort_by_item': sort.item,
    'sort_by_dir':  sort.dir,
    'sort':         sort,
    'dhiv': 'dhiv' in request.GET,
    'dhcv': 'dhcv' in request.GET,
    'dhbv': 'dhbv' in request.GET,
    'visit_date': 'visit_date' in request.GET,
    'no_of_reports': p.reports_max,
    'single_access': ReportViews(request).single_access # this allows reports/ to auto-forward requests for users with only 1 view
  }
  return dict(default_view.items() + ret.items())

def entry (request, default_view={}):
  rv = ReportViews(request)
  if rv.single_access == True:
      if rv.avrc == True:
          return HTTPFound(request.route_path('reports-avrc'))
      elif rv.oakland == True:
          return HTTPFound(request.route_path('reports-oakland'))
      elif rv.emory == True:
          return HTTPFound(request.route_path('reports-emory'))
  ret = {
      'admins': rv.admins,
      'avrc': rv.avrc,
      'oakland': rv.oakland,
      'emory': rv.emory,
      'single_access': rv.single_access
  }
  return dict(default_view.items() + ret.items())

@view_config(route_name='reports', renderer='templates/pages/report-entry.pt', permission='reports')
def reports_view(request):
  return entry(request, default_view=default_view(request))

@view_config(route_name='reports-admins', renderer='templates/pages/reports.pt', permission='admins')
def reports_admin_view(request):
  return process(request, 'admins', default_view=default_view(request))

@view_config(route_name='reports-avrc', renderer='templates/pages/reports.pt', permission='avrc')
def reports_avrc_view(request):
  return process(request, 'avrc', default_view=default_view(request))

@view_config(route_name='reports-oakland', renderer='templates/pages/reports.pt', permission='oakland')
def reports_oakland_view(request):
  return process(request, 'oakland', default_view=default_view(request))

@view_config(route_name='reports-emory', renderer='templates/pages/reports.pt', permission='emory')
def reports_emory_view(request):
  return process(request, 'emory', default_view=default_view(request))

@view_config(route_name='reports-admins-excel', permission='admins')
def reports_admin_excel_view(request):
  return process(request, 'admins', csv_export=True)

@view_config(route_name='reports-avrc-excel', permission='avrc')
def reports_avrc_excel_view(request):
  return process(request, 'avrc', csv_export=True)

@view_config(route_name='reports-oakland-excel', permission='oakland')
def reports_oakland_excel_view(request):
  return process(request, 'oakland', csv_export=True)

@view_config(route_name='reports-emory-excel', permission='emory')
def reports_emory_excel_view(request):
  return process(request, 'emory', csv_export=True)

