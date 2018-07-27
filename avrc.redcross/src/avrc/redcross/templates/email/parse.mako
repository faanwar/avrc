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

Red Cross test result updates for site: ${site_code}

Date import occurred: ${timestamp.strftime('%Y-%m-%d at %I:%M %p')}

${type_.upper()} Positive: ${len(pnt)}
Other: ${len(odd)}

---------------------------------------
RCID List ${determine_site(code)} \
---------------------------------------

${positive_result(pnt)}



<%def name="determine_site(code)">\
code
\
% endif
</%def>\

<%def name="positive_result(items)">\
% if items:
The list of ${len(items)} positive records follows:
${results2table(items)}
% else:
\
% endif
\
</%def>\

def formateach(iterable):
  for r in iterable:
    yield [
      r['rc_id'], r['visit_date']]

def results2table(iterable):
  return tabulate(formateach(iterable))

