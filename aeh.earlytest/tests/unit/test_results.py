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

class TestProcess(IntegrationFixture):

  def test_no_draw_date(self):
    """
    It should report the results are not available if nat is P and dhiv is NT
    """
    from aeh.earlytest.results import process
    from datetime import date
    from aeh.earlytest import Session, models

    site_code = '99X'
    reference_number = '12345'
    expected = site_code + reference_number

    Session.add(
        models.Result(
            site_code=site_code,
            reference_number=reference_number,
            test_date=date.today(),
            nat='P',
            file='results.txt'))

    request = DummyRequest({
        'userInput1': ' '.join(list(site_code + reference_number)),
        'userInput2': site_code + ' ' + reference_number
        })

    ret = process(request)
    self.assertEquals(ret['queryStatus'], 'RESULTS_NOT_AVAILABLE')

  def test_dhiv_not_tested(self):
    """
    It should report the results are not available if nat is P and dhiv is NT
    """
    from aeh.earlytest.results import process
    from datetime import date
    from aeh.earlytest import Session, models

    site_code = '99X'
    reference_number = '12345'
    expected = site_code + reference_number

    Session.add(
        models.Result(
            site_code=site_code,
            reference_number=reference_number,
            test_date=date.today(),
            draw_date=date.today(),
            nat='P',
            dhiv='NT',
            file='results.txt'))

    request = DummyRequest({
        'userInput1': ' '.join(list(site_code + reference_number)),
        'userInput2': site_code + ' ' + reference_number
        })

    ret = process(request)
    self.assertEquals(ret['queryStatus'], 'RESULTS_NOT_AVAILABLE')

  def test_valid(self):
    """
    It should be able to parse a number with whitespace in it
    """
    from aeh.earlytest.results import process
    from datetime import date
    from aeh.earlytest import Session, models

    site_code = '99X'
    reference_number = '12345'
    expected = site_code + reference_number

    Session.add(
        models.Result(
            site_code=site_code,
            reference_number=reference_number,
            test_date=date.today(),
            draw_date=date.today(),
            nat='N',
            file='results.txt'))

    request = DummyRequest({
        'userInput1': ' '.join(list(site_code + reference_number)),
        'userInput2': site_code + ' ' + reference_number
        })

    ret = process(request)
    self.assertEquals(ret['defaultNumber'], expected)
    self.assertEquals(ret['cleanNumber1'], expected)
    self.assertEquals(ret['cleanNumber2'], expected)

  def test_invalid(self):
    """
    It should fail if inputs are not equal
    """
    from aeh.earlytest.results import process
    from datetime import date
    from aeh.earlytest import Session, models

    site_code = '99X'
    reference_number = '12345'

    Session.add(
        models.Result(
            site_code=site_code,
            reference_number=reference_number,
            test_date=date.today(),
            draw_date=date.today(),
            nat='N',
            file='results.txt'))

    request = DummyRequest({
        'userInput1': site_code + reference_number,
        'userInput2': 'LOL' + ' ' + reference_number
        })

    ret = process(request)
    self.assertEquals(ret['queryStatus'], 'QUERY_INVALID')

  def test_positive(self):
    """
    It should not let the user know if they are HIV positive
    (This will be done in person)
    """
    from aeh.earlytest.results import process
    from datetime import date
    from aeh.earlytest import Session, models

    site_code = '99X'
    reference_number = '12345'
    expected = site_code + reference_number

    Session.add(
        models.Result(
            site_code=site_code,
            reference_number=reference_number,
            test_date=date.today(),
            draw_date=date.today(),
            nat='P',
            dhiv='P',
            file='results.txt'))

    request = DummyRequest({
        'userInput1': expected,
        'userInput2': expected,
        })

    ret = process(request)
    self.assertEquals(ret['queryStatus'], 'RESULTS_NOT_AVAILABLE')

  def test_negative_not_available(self):
    """
    It should not report the patient's status before 14 days of draw date
    """
    from aeh.earlytest.results import process
    from datetime import date
    from aeh.earlytest import Session, models

    site_code = '99X'
    reference_number = '12345'
    expected = site_code + reference_number

    result = models.Result(
        site_code=site_code,
        reference_number=reference_number,
        test_date=date.today(),
        draw_date=date.today(),
        nat='N',
        file='results.txt')
    Session.add(result)

    request = DummyRequest({
        'userInput1': expected,
        'userInput2': expected,
        })

    ret = process(request)
    self.assertEquals(ret['queryStatus'], 'RESULTS_NOT_AVAILABLE')

  def test_negative_available(self):
    """
    It should report the patient's status after 14 days of draw date
    """
    from aeh.earlytest.results import process
    from datetime import date, timedelta
    from aeh.earlytest import Session, models

    site_code = '99X'
    reference_number = '12345'
    expected = site_code + reference_number

    result = models.Result(
        site_code=site_code,
        reference_number=reference_number,
        test_date=date.today() - timedelta(14),
        draw_date=date.today() - timedelta(14),
        nat='N',
        file='results.txt')
    Session.add(result)

    request = DummyRequest({
        'userInput1': expected,
        'userInput2': expected,
        })

    ret = process(request)
    self.assertEquals(ret['queryStatus'], 'RESULTS_NEGATIVE')

  def test_unavailable(self):
    """
    It should not report the patient's status after 90 days
    """
    from aeh.earlytest.results import process
    from datetime import date, timedelta
    from aeh.earlytest import Session, models

    site_code = '99X'
    reference_number = '12345'
    expected = site_code + reference_number

    Session.add(
        models.Result(
            site_code=site_code,
            reference_number=reference_number,
            test_date=date.today() - timedelta(90),
            draw_date=date.today() - timedelta(90),
            nat='N',
            file='results.txt'))

    request = DummyRequest({
        'userInput1': expected,
        'userInput2': expected,
        })

    ret = process(request)
    self.assertEquals(ret['queryStatus'], 'RESULTS_OUT_OF_DATE')

  def test_not_found(self):
    """
    It should report "not found" if the result is not in the database
    """
    from aeh.earlytest.results import process

    site_code = '99X'
    reference_number = '12345'
    expected = site_code + reference_number

    request = DummyRequest({
        'userInput1': expected,
        'userInput2': expected,
        })

    ret = process(request)
    self.assertEquals(ret['queryStatus'], 'RESULTS_NOT_FOUND')

