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

class TestDrawDateInput(IntegrationFixture):

  def test_is_number(self):
    """
    It should return true if it's a string of numbers
    It should return false if it's not a string of numbers
    """
    from aeh.earlytest.draw_input import is_number

    ref_num = "12345"
    self.assertTrue(is_number(ref_num))

    ref_num_char = "abcde"
    self.assertFalse(is_number(ref_num_char))

    ref_num_and_char = "123C4"
    self.assertFalse(is_number(ref_num_and_char))


  def test_check_format(self):
    """
    It should return true when the rcid is in the correct format.
    It should return false when the rcid is in the incorrect format.
    76GH#####
    76C#####
    """
    from aeh.earlytest.draw_input import check_format, is_number

    # Correct RCID formats should return true
    site_code_c = "76C"
    site_code_gh = "76GH"
    site_code_c_lower = "76c"
    site_code_gh_lower = "76gh"
    ref_num = "12345"

    self.assertTrue(check_format(site_code_c, ref_num))
    self.assertTrue(check_format(site_code_gh, ref_num))
    self.assertTrue(check_format(site_code_c_lower, ref_num))
    self.assertTrue(check_format(site_code_gh_lower, ref_num))

    # Incorrect RCID formats should return false
    site_code_b = "76B"
    site_code_many_char = "76CCCC"
    site_code_just_char = "GHC"
    ref_num_many = "12345678"
    ref_num_few = "123"
    ref_num_char = "abcde"

    self.assertFalse(check_format(site_code_b, ref_num))
    self.assertFalse(check_format(site_code_many_char, ref_num))
    self.assertFalse(check_format(site_code_just_char, ref_num))
    self.assertFalse(check_format(site_code_c, ref_num_many))
    self.assertFalse(check_format(site_code_c, ref_num_few))
    self.assertFalse(check_format(site_code_c, ref_num_char))
    self.assertFalse(check_format(site_code_gh, ref_num_many))
    self.assertFalse(check_format(site_code_gh, ref_num_few))
    self.assertFalse(check_format(site_code_gh, ref_num_char))

  def test_invalid_format_error_status(self):
    """
    Should fail and set error_status = incorrectFormat
    """
    from aeh.earlytest.draw_input import process
    from datetime import date
    from aeh.earlytest import Session, models

    site_code = '99X'
    reference_number = '11111'
    expected = site_code + reference_number
    draw_date = '2015-01-01'

    request = DummyRequest({
        'redcrossid-entry': expected,
        'drawdate-input': draw_date,
        'rcidform.submitted': True,
        })

    ret = process(request)

    print("We get", ret['errorStatus'])

    self.assertEquals(ret['errorStatus'], 'incorrectFormat')

  def test_valid_entry_error_status(self):
    """
    Should pass and set error_status = rcidAccepted
    """
    from aeh.earlytest.draw_input import process
    from datetime import date
    from aeh.earlytest import Session, models

    site_code = '76C'
    reference_number = '22222'
    expected = site_code + reference_number
    draw_date = '2015-01-01'

    request = DummyRequest({
        'redcrossid-entry': expected,
        'drawdate-input': draw_date,
        'rcidform.submitted': True,
        })

    ret = process(request)
    self.assertEquals(ret['errorStatus'], 'rcidAccepted')

  def test_duplicate_entry_error_status(self):
    """
    Should fail and set error_status = duplicateEntry
    """
    from aeh.earlytest.draw_input import process
    from datetime import date
    from aeh.earlytest import Session, models

    site_code = '76C'
    reference_number = '33333'
    expected = site_code + reference_number
    draw_date = '2015-01-01'

    Session.add(
        models.Draw(
            site_code=site_code,
            reference_number=reference_number,
            draw_date=date.today(),))

    request = DummyRequest({
        'redcrossid-entry': expected,
        'drawdate-input': draw_date,
        'rcidform.submitted': True,
        })

    ret = process(request)
    self.assertEquals(ret['errorStatus'], 'duplicateEntry')

  def test_valid_entry_update_database(self):
    """
    Should pass and the entry gets saved in draw table
    """
    from aeh.earlytest.draw_input import process
    from datetime import date
    from datetime import datetime
    from aeh.earlytest import Session, models

    site_code = '76C'
    reference_number = '44444'
    expected = site_code + reference_number
    draw_date = '2015-01-01'

    request = DummyRequest({
        'redcrossid-entry': expected,
        'drawdate-input': draw_date,
        'rcidform.submitted': True,
        })

    ret = process(request)
    self.assertEquals(ret['errorStatus'], 'rcidAccepted')

    draw = Session.query(models.Draw)\
    			.filter(models.Draw.site_code == site_code)\
    			.filter(models.Draw.reference_number == reference_number).first()

    self.assertTrue(draw)
    self.assertEquals(draw.site_code, site_code)
    self.assertEquals(draw.reference_number, reference_number)
    self.assertEquals(draw.draw_date, datetime.date(datetime.strptime(draw_date, "%Y-%m-%d")))
  def test_valid_entry_update_result_draw_date(self):
    """
    Should pass, save entry in draw table, and update draw date in corresponding result
    entry in result table
    """
    from aeh.earlytest.draw_input import process
    from datetime import date
    from datetime import datetime
    from aeh.earlytest import Session, models

    site_code = '76C'
    reference_number = '55555'
    expected = site_code + reference_number
    draw_date = '2015-01-01'

    Session.add(
        models.Result(
            site_code=site_code,
            reference_number=reference_number,
            test_date=date.today(),
            nat='N',
            file='results.txt'))

    request = DummyRequest({
        'redcrossid-entry': expected,
        'drawdate-input': draw_date,
        'rcidform.submitted': True,
        })

    ret = process(request)
    self.assertEquals(ret['errorStatus'], 'rcidAccepted')

    draw = Session.query(models.Draw)\
    			.filter(models.Draw.site_code == site_code)\
    			.filter(models.Draw.reference_number == reference_number).first()

    self.assertEquals(draw.site_code, site_code)
    self.assertEquals(draw.reference_number, reference_number)
    self.assertEquals(draw.draw_date, datetime.date(datetime.strptime(draw_date, "%Y-%m-%d")))

    result = Session.query(models.Result)\
    			.filter(models.Result.site_code == site_code)\
    			.filter(models.Result.reference_number == reference_number).first()

    self.assertEquals(result.draw_date, datetime.date(datetime.strptime(draw_date, "%Y-%m-%d")))
