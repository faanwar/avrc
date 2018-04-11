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

import os.path
try:
  import unittest2 as unittest
except ImportError:
  import unittest

HERE = os.path.abspath(os.path.dirname(__file__))
TEST_INI = os.path.join(HERE, 'app.ini')


class IntegrationFixture(unittest.TestCase):
  """
  Fixure for testing component integration
  """

  @classmethod
  def setUpClass(cls):
    from pyramid.paster import get_appsettings
    from sqlalchemy import engine_from_config
    from aeh.earlytest import Session, models
    cls.settings = settings = get_appsettings(TEST_INI)
    Session.configure(bind=engine_from_config(settings, 'sqlalchemy.'))
    models.Base.metadata.create_all(Session.bind)

  @classmethod
  def tearDownClass(cls):
    drop_db()
    disconnect_db()

  def setUp(self):
    from pyramid import testing
    self.config = testing.setUp()

  def tearDown(self):
    from pyramid import testing
    import transaction
    testing.tearDown()
    transaction.abort()


class FunctionalFixture(unittest.TestCase):
  """
  Fixture for testing the full application stack.
  Tests under this fixture will be very slow, so use sparingly.
  """

  @classmethod
  def setUpClass(cls):
    from pyramid.paster import get_app
    cls.app = get_app(TEST_INI)

  def setUp(self):
    from webtest import TestApp
    self.app = TestApp(self.app)
    create_db()

  def tearDown(self):
    drop_db()
    disconnect_db()


def create_db():
  from aeh.earlytest import Session, models
  models.Base.metadata.create_all(Session.bind)


def drop_db():
  from aeh.earlytest import Session, models
  models.Base.metadata.drop_all(Session.bind)


def disconnect_db():
  from aeh.earlytest import Session
  Session.remove()
