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

from pyramid.config import Configurator
from sqlalchemy import orm
from sqlalchemy import engine_from_config
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker, relation
from zope.sqlalchemy import ZopeTransactionExtension
import transaction
import ldap

from pyramid.authentication import AuthTktAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from pyramid_ldap import groupfinder
from aeh.earlytest import models
import ConfigParser, json
import logging
import turbomail
# With Pycap there is no need for an orm session
redcap_settings = None
Session = orm.scoped_session(
            orm.sessionmaker(extension=ZopeTransactionExtension()))
Config = ConfigParser.ConfigParser();
mail_settings = None
log = None
#Session = orm.scoped_session(orm.sessionmaker())

def main(global_config, **settings):
  Config.read(global_config['__file__'])

  """ This function returns a Pyramid WSGI application.
  """
  
  engine = engine_from_config(settings, 'sqlalchemy.')
  Session.configure(bind=engine)

  # Read the redcap information using 'redcap.json' file
  global redcap_settings
  redcap_settings = json.loads(open(settings['redcap_json'], 'r').read())

  global log
  try:
    if settings['logging_enabled'] == 'true':
      log = logging.getLogger(__name__)
  except KeyError:
    pass
    
  global mail_settings
  mail_settings = dict(Config.items('aeh:mail'))
  turbomail.interface.start(mail_settings)

  authn_policy = AuthTktAuthenticationPolicy(
    settings['secret'], callback=groupfinder, hashalg='sha512', timeout=600)
  authz_policy = ACLAuthorizationPolicy()

  config = Configurator(settings=settings,
                        root_factory=models.RootFactory)
  config.set_authentication_policy(authn_policy)
  config.set_authorization_policy(authz_policy)

  config.include("pyramid_tm")
  config.include("pyramid_ldap")
  config.include("pyramid_rewrite")
  config.include("pyramid_chameleon")

  config.add_static_view('static', 'static', cache_max_age=3600)
  config.add_translation_dirs('aeh.earlytest:locale')
  #temp bandaid, insecure because it accepts all self-signed cert.
  #old server should have cert saved so remove this bandaid after port
  #We could also save the cert in ticino
  ldap.set_option(ldap.OPT_X_TLS_REQUIRE_CERT, ldap.OPT_X_TLS_NEVER)

  config.ldap_setup(
    settings['ldap.host'],
    bind=settings['ldap.binddn'],
    passwd=settings['ldap.bindpw'],
    )

  config.ldap_set_login_query(
    base_dn=settings['ldap.users_basedn'],
    filter_tmpl="(mail=%(login)s)",
    scope = ldap.SCOPE_SUBTREE,
    )

  config.ldap_set_groups_query(
    base_dn=settings['ldap.group_basedn'],
    filter_tmpl="(&(objectClass=groupOfNames)(member=%(userdn)s))",
    scope=ldap.SCOPE_SUBTREE,
    cache_period=600,
    )

  config.add_rewrite_rule(r'/(?P<path>.*)/', r'/%(path)s')

  route = config.add_route
  route('home', '/')
  route('about', '/about')
  route('faqs', '/faqs')
  route('location', '/location')
  route('results', '/results')
  route('locale', '/locale/{language}')
  route('reports', '/reports')
  route('reports-avrc', 'reports/avrc')
  route('reports-avrc-excel', 'reports/avrc/excel')
  route('reports-oakland', 'reports/oakland')
  route('reports-oakland-excel', 'reports/oakland/excel')
  route('reports-emory', 'reports/emory')
  route('reports-emory-excel', 'reports/emory/excel')
  route('reports-admins', 'reports/admin')
  route('reports-admins-excel', 'reports/admin/excel')
  route('reports-partner', 'reports/partner')
  route('reports-partner-excel', 'reports/partner/excel')
  route('reports-uni', 'reports/uni')
  route('reports-uni-excel', 'reports/uni/excel')
  route('login', '/login')
  route('logout', '/logout')
  route('testingfortickets', '/testingfortickets')
  route('unsubscribe', '/unsubscribe')
  route('update-date', 'reports/admin/update_date')
  route('otp','/otp'); 

  config.scan()
  return config.make_wsgi_app()
