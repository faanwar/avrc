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
from pyramid.view import forbidden_view_config
from .views import default_view
from aeh.earlytest import models

import ldap

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy

from pyramid.view import (
  view_config,
  forbidden_view_config,
)

from pyramid.httpexceptions import HTTPFound

from pyramid.security import (
  Allow,
  Authenticated,
  remember,
  forget,
)

from pyramid_ldap import (
  get_ldap_connector,
  groupfinder,
)

from pyramid.security import remember
from pyramid.security import forget

def process(request, view_items):
  login_url = request.route_path('login')
  referrer = request.url
  if referrer == login_url:
    referrer = '/' # never use the login form itself as came_from
  came_from = request.params.get('came_from', referrer)
  message = ''
  login = ''
  if 'form.submitted' in request.params:
    login = request.params['login']
    password = request.params['password']
    connector = get_ldap_connector(request)
    data = connector.authenticate(login, password)
    if data is not None:
      dn = data[0]
      groups = connector.user_groups(dn)
      if groups:
        for u in groups:
          # check to ensure the dn is an ET member before allowing any further...
          if models.members_cn == u[0]:
            headers = remember(request, dn)
            return HTTPFound(location=came_from, headers=headers)
      message = "Your credentials are correct but your account does not have sufficient permission to access this page. Please contact your system administrator."
    else:
      message = "Invalid username or password. Please try again or contact your system administrator."

  out = {
    'message': message,
    'url' : request.route_path("login"),
    'came_from': came_from,
    'login': login,
  }
  return dict(view_items.items()+out.items())

@view_config(route_name='login', renderer='templates/pages/login.pt')
@forbidden_view_config(renderer='templates/pages/login.pt')
def login_view(request):
    return process(request, default_view(request,"login"))

@view_config(route_name='logout')
def logout_view(request):
  headers = forget(request)
  return HTTPFound(location = request.route_path('home'), headers = headers)
