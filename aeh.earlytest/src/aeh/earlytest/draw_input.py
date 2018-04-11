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
from pyramid.httpexceptions import HTTPFound
import datetime

# check_format(site_code, ref_num)
# Purpose: This function accepts two strings. It checks whether the site_code
# and the ref_num is in the appropriate formats. Returns true if it's in correct format.
# Returns false otherwise.
# 76C#####
# 76GH#####
def check_format(site_code, ref_num):
    # Checking the site_code
    if site_code.lower() == "76c" or site_code.lower() == "76gh" or site_code.lower() == "76fj":
        # Checking if ref_num is length 5
        if len(ref_num) == 5:
            return is_number(ref_num)

    return False

# is_number(s)
# Purpose: This function accepts a string and checks if it is a string of numbers.
# Returns true if it is a list of numbers. Returns false otherwise.
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

# parse_input(text)
# Purpose: This function accepts a string, removes all whitespaces, strips the string into the
# site code and reference number. It returns a dictionary with the site code and reference number.
def parse_input(text):
    strip_text = text.replace(' ','')
    offset = len(strip_text) - 5
    site_code = strip_text[:offset].upper()
    ref_num   = strip_text[offset:]

    return { 'site_code': site_code, 'ref_num': ref_num }

# process(request, default_view={})
# Purpose: This function accepts a request and the default view. It processes user submissions to determine
# appropriate actions. If the RCID is valid, it notifies the user that the RCID has been saved into the database.
# If the RCID is invalid, it notifies the user of what to do next.
def process(request, default_view={}):
    error_status = ''
    site_code = ''
    ref_num = ''
    draw_date = ''
    draw_date_raw = ''

    # Calculate min and max attributes for draw-input.pt page
    max_date = datetime.date.today()
    min_date = max_date - datetime.timedelta(days=365)

    max_date = max_date.strftime("%Y-%m-%d")
    min_date = min_date.strftime("%Y-%m-%d")
    if 'rcidform.submitted' in request.params:
        redcrossid = parse_input(request.params['redcrossid-entry'])
        site_code = redcrossid['site_code']
        ref_num   = redcrossid['ref_num']
        draw_date_raw = request.params['drawdate-input']
        draw_date = datetime.datetime.strptime(draw_date_raw, "%Y-%m-%d").date()

        # Check if red cross id is in correct format
        if not check_format(site_code, ref_num):
            #Error. Incorrect red cross id format
            error_status = "incorrectFormat"
        else:
            session = Session()
            draw = session.query(models.Draw)\
                     .filter(models.Draw.site_code == site_code)\
                     .filter(models.Draw.reference_number == ref_num).first()
            #check if it exists in the database
            if not draw:
                #Sucess! Save the entry in the draw database
                new_draw_entry = models.Draw(
                site_code=site_code,
                reference_number=ref_num,
                draw_date=draw_date,
                has_result=int(0)
                )
                session.add(new_draw_entry)
                transaction.commit()

                error_status = "rcidAccepted"

                #Check if this draw's rcid is currently in our results table. If so, update
                #the result's draw date.
                result = session.query(models.Result)\
                            .filter(models.Result.site_code == site_code)\
                            .filter(models.Result.reference_number == ref_num).first()
                if result:
                    result.draw_date = draw_date

                    # Update has_result status of the draw date entry to True
                    draw_entry = session.query(models.Draw)\
                            .filter(models.Draw.site_code == site_code)\
                            .filter(models.Draw.reference_number == ref_num).first()
                    draw_entry.has_result = int(1)

                    transaction.commit()

            else:
                #Error. Duplicate entry
                error_status = "duplicateEntry"

    ret = {
      'defaultNumber': site_code + ref_num,
      'errorStatus' : error_status,
      'drawDate': draw_date,
      'drawDateRaw': draw_date_raw,
      'maxDate': max_date,
      'minDate': min_date,
    }

    return dict(default_view.items() + ret.items())


#@view_config(route_name='draw-input', renderer='templates/pages/draw-input.pt', permission='draw-input')
def rcidinput_view(request):
    return process(request, default_view=default_view(request))

