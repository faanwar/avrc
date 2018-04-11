## This software is Copyright (c) 2015,
## The Regents of the University of California.
##
## Developed by the UCSD CFAR BIT Core (bitcore@ucsd.edu)
##
## Core Developers:
##   Sergei L Kosakovsky Pond (spond@ucsd.edu)
##   Jason A Young (jay007@ucsd.edu)
##   Marco A Martinez (mam002@ucsd.edu)
##   Steven Weaver (sweaver@ucsd.edu)
##   Zachary Smith (z4smith@ucsd.edu)
##
## Significant contributions from:
##   David Mote (davidmote [at] gmail [dot] com)
##   Jennifer Rodriguez-Mueller (almostlikethat [at] gmail [dot] com)
##   Drew Allen (asallen@ucsd.edu)
##   Andrew Dang (a7dang [at] gmail [dot] com)
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
## * Redistributions of source code must retain the above copyright notice, this
##   list of conditions and the following disclaimer.
##
## * Redistributions in binary form must reproduce the above copyright notice,
##   this list of conditions and the following disclaimer in the documentation
##   and/or other materials provided with the distribution.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
## ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
## LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
## CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
## SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
## INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
## CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
## ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
## POSSIBILITY OF SUCH DAMAGE.

---------------------------------------------
New Red Cross Results Available For Site ${determine_site(code)} \
---------------------------------------------

Results of 'AEH-Redcross update' as of ${timestamp.strftime('%Y-%m-%d at %I:%M %p')}:

${summary_redcross_update(results_count)}\

---------------------------------------
Missing Draw Dates Update For Site ${determine_site(code)} \
---------------------------------------

${summary_missing_draw_txt(missing_draw_count)}
\
${summary_missing_draw(missing_draw, title='MISSING DRAW DATES')}
\
----------------------------------------------
Missing Red Cross Results Update For Site ${determine_site(code)} \
----------------------------------------------

${summary_missing_result_txt(missing_results_count, days_till_notify)}
\
${summary_missing_result(missing_results, title='MISSING RESULTS')}
\
<%include file="footer.mako"/>\
<%!
from tabulate import tabulate

HEADERS_MISSING_DRAW = ['RCID', 'TEST DATE']
HEADERS_MISSING_RESULT = ['RCID', 'VISIT DATE']

def formateach_missing_draw(iterable):
  for r in iterable:
    yield [
      str(r.site_code)+str(r.reference_number), r.test_date]

def formateach_missing_result(iterable):
  for r in iterable:
    yield [
      r['rc_id'], r['visit_date']]

def results2table_missing_draw(iterable):
  return tabulate(formateach_missing_draw(iterable), headers=HEADERS_MISSING_DRAW)

def results2table_missing_result(iterable):
  return tabulate(formateach_missing_result(iterable), headers=HEADERS_MISSING_RESULT)
%>\
<%def name="summary_missing_draw(items, title)">\
% if items:
The list of ${len(items)} ${title} records follows:
${results2table_missing_draw(items)}
% else:
\
% endif
\
</%def>\

<%def name="summary_redcross_update(count)">\
% if count > 0:
We received ${count} Red Cross Result(s), and these result(s) were successfully uploaded to the database. You may view these result(s) on this webpage http://theearlytest.ucsd.edu/reports

Site specific positive results were emailed to the appropriate recipients.
% else:
There are NO new Red Cross results for your site in this recent upload. 
\
% endif
</%def>\

<%def name="summary_missing_result(items, title)">\
% if items:
The list of ${len(items)} ${title} records follows:
${results2table_missing_result(items)}
% else:
\
% endif
\
</%def>\

<%def name="summary_missing_draw_txt(count)">\
% if count > 0:
${count} Red Cross Result(s) do NOT have a matching Draw Date. 

This means that the Red Cross IDs and their corresponding draw/visit dates were not entered into this webpage https://redcap.ucsd.edu/ 

Please enter them so that these results for these clients are available in a timely manner.
% else:
There are NO missing Draw Dates.
\
% endif
</%def>\

<%def name="summary_missing_result_txt(count, days_till_notify)">\
% if count > 0:
${count} Draw Date entries do NOT have a Red Cross Result for over ${days_till_notify} days.

Please contact the testing manager David Rodriguez (dar002@ucsd.edu).
% else:
There are NO missing Red Cross Results.
\
% endif
</%def>\

<%def name="determine_site(code)">\
% if code == "76C":
AVRC
% elif code == "76GH":
Oakland
% elif code == "76FJ":
Emory
\
% endif
</%def>\
