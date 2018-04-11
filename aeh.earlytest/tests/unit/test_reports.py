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

from pyramid.testing import DummyRequest
from tests import IntegrationFixture

class TestReports(IntegrationFixture):

  def test_generate_slice(self):
    """
    Ensure pages convert to result start & end points correctly
    """
    from aeh.earlytest.reports import generate_slice_values

    page = 10
    results_per_page = 10

    ret = generate_slice_values(page, results_per_page)
    self.assertEquals(ret['start'], 90)
    self.assertEquals(ret['end'], 99)

  def test_generate_site(self):
    """
    Generate a name and list of codes for a provided permission level
    """
    from aeh.earlytest.reports import ReportSite

    permissions = 'admins'
    ret = ReportSite(permissions)
    self.assertEquals(ret.name, "AVRC & Oakland")
    self.assertEquals(ret.codes, ['76C','76GH'])

    permissions = 'avrc'
    ret = ReportSite(permissions)
    self.assertEquals(ret.name, "AVRC")
    self.assertEquals(ret.codes, ['76C'])

    permissions = 'oakland'
    ret = ReportSite(permissions)
    self.assertEquals(ret.name, "Oakland")
    self.assertEquals(ret.codes, ['76GH'])

  def test_generate_conditions (self):
    """
    Generate a conditions list for querying based on search settings
    """
    from aeh.earlytest.reports import generate_conditions
    #
    # should show all results
    #
    request = DummyRequest({
    })
    ret = generate_conditions(request,['99X'])
    self.assertEquals(str(ret),"result.site_code IN (:site_code_1)")

    #
    # should show only positive and missing results
    #
    request = DummyRequest({
      'hivp': 'True',
      'hcvp': 'True',
      'hbvp': 'True',
      'miss': 'True'
    })
    ret = generate_conditions(request,['99X'])
    self.assertEquals(str(ret),"result.dhiv = :dhiv_1 AND result.dhcv = :dhcv_1 AND result.dhbv = :dhbv_1 AND result.draw_date IS NULL AND result.site_code IN (:site_code_1)")

    #
    # should show only HIV positive
    #
    request = DummyRequest({
      'hivp': 'True',
      'hbvp': 'True'
    })
    ret = generate_conditions(request,['99X'])
    self.assertEquals(str(ret),"result.dhiv = :dhiv_1 AND result.dhbv = :dhbv_1 AND result.site_code IN (:site_code_1)")

  def test_generate_reports (self):
    """
    Generate a conditions list for querying based on search settings
    """
    from aeh.earlytest.reports import generate_reports

    #
    # only error will be produced here...
    #
    ret = generate_reports('',0,10)
