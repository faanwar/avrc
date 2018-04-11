## This software is Copyright (c) 2015,
## The Regents of the University of California.
##
## Developed by the UCSD CFAR BIT Core (bitcore@ucsd.edu)
##
## Core Developers:
## Ajay Mohan ajmohan@ucsd.edu
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
Daily RedCAP DB Status Check For Site ${determine_site(code)} \
---------------------------------------------

Results of 'RedCAP and Earlytest Sync' as of ${timestamp.strftime('%Y-%m-%d at %I:%M %p')}:

---------------------------------------
Missing Draw Dates Update For Site ${determine_site(code)} \
---------------------------------------

${summary_missing_draw_txt(report_date_count)}
\
${summary_missing_draw(report_date, level, days_till_urgent, title='MISSING DRAW DATES')}
\
\
<%include file="footer.mako"/>\
<%!
from tabulate import tabulate

HEADERS_MISSING_DRAW = ['RCID', 'TEST DATE']

def formateach_missing_draw(iterable):
  for r in iterable:
    yield [
      str(r.site_code)+str(r.reference_number), r.test_date]

def results2table_missing_draw(iterable):
  return tabulate(formateach_missing_draw(iterable), headers=HEADERS_MISSING_DRAW)

%>\

<%def name="summary_missing_draw(items, level, days_till_urgent, title)">\
% if items and level ==1:
Warning, The following Draw Dates are missing for over a period of ${days_till_urgent} days since receiving the results. 
The list of ${len(items)} ${title} records follows:
${results2table_missing_draw(items)}
% elif items and level == 2:
Critical, The following Draw Dates are missing for over a period of ${int(days_till_urgent)+2} days after receiving the results.
The list of ${len(items)} ${title} records follows:
${results2table_missing_draw(items)}
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
