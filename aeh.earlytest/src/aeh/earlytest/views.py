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

from pyramid.view import view_config
from pyramid.renderers import get_renderer
from aeh.earlytest import results
from aeh.earlytest import locale
from aeh.earlytest import redcap_settings as rcs
from avrc.redcross import RCProject, log
from pyramid.security import authenticated_userid
from pyramid.security import Allowed
from pyramid.httpexceptions import HTTPFound
import traceback

def default_view(request, default_active='', template='templates/master.pt'):
  renderer = get_renderer(template)
  logged_in = ''
  
  if authenticated_userid(request):
    logged_in = "an Authenticated User"
    #logged_in = authenticated_userid(request)

  return \
  {
    'project'        : 'aeh.earlytest',
    'language'       : request._LOCALE_,
    'main_template'  : renderer.implementation().macros['main_template'],
    'default_active' : default_active,
    'logged_in'      : logged_in
  }


def unsubscribe_view(request, default_active='', template='templates/master.pt'):
  renderer = get_renderer(template)
  message = "We are so sorry your request could not be completed. Please contact leadtheway@ucsd.edu if you need assistance."
  email = 'your_email@domain.com'
  url = ''
  substatus = 500
  rc_id = ''

  try:
    if 'unsubscribe.submitted' in request.params:
      email = request.params['email']
      url = request.route_path("unsubscribe")
      rc_id = request.params['rc_id']

      if rc_id == None and email == None:
        raise

      site = rc_id[:-5].upper()
      redcap = RCProject([site], rcs)
      fields = ['rc_id', 'testing_reminder']
      records = redcap.project[site].export_records(records=[rc_id], fields=fields)
      if len(records) == 1:
        if records[0]['testing_reminder'] == u'1':
          records[0]['testing_reminder'] = u'0'
          if redcap.project[site].import_records(records) == 0:
            raise
          message = "Your email address " + email + " has been successfully removed from our mailing list."
          substatus = 200        
          
        else:
          message = "Our records indicate " + email + " is not subscribed to receive any emails. Please contact goodtogo@ucsd.edu if you need assistance."
          substatus = 200
      else:
        message = "Test ID Unknown. Please contact goodtogo@ucsd.edu if you need assistance."
      

  except:
    log.debug(traceback.format_exc())

  return \
    {
      'project'        : 'aeh.earlytest',
      'language'       : request._LOCALE_,
      'main_template'  : renderer.implementation().macros['main_template'],
      'default_active' : default_active,
      'logged_in'      : '',
      'message'        : message,
      'email'          : email,
      'url'            : url,
      'rc_id'          : rc_id,
      'substatus'      : substatus
    }

@view_config(route_name='locale', renderer='templates/pages/home.pt')
def locale_view(request):
  request.view = 'home'
  return locale.process(request)

@view_config(route_name='home', renderer='templates/pages/home.pt')
def home_view(request):
  return default_view(request,"about")

@view_config(route_name='about', renderer='templates/pages/home.pt')
def about_view(request):
  return default_view(request,"about")

@view_config(route_name='faqs', renderer='templates/pages/faqs.pt')
def faqs_view(request):
  return default_view(request,"faqs")

@view_config(route_name='location', renderer='templates/pages/location.pt')
def location_view(request):
  return default_view(request,"location")

@view_config(route_name='results', renderer='templates/pages/results.pt')
def results_view(request):
  return results.process(request, default_view=default_view(request,"results"))

@view_config(route_name='otp', renderer='templates/pages/otp.pt')
def otp_view(request):
  return results.otp_entry(request, default_view=default_view(request,"otp"))

@view_config(route_name='unsubscribe', renderer='templates/pages/unsubscribe.pt')
def unsub_view(request):
  return unsubscribe_view(request,"unsubscribe")

@view_config(route_name='contact', renderer='templates/pages/contact.pt')
def contact_view(request):
  return default_view(request,"contact")

