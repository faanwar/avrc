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
#   Zachary Smith (z4smith@ucsd.edu)
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

from nose.tools import raises, eq_

from avrc.redcross.models import check_pnt, Result, Draw


nat_tests = (
    ((None, None), None),
    (('P', None), None),
    (('P', 'P'), True),
    (('P', 'N'), False),
    (('P', 'NT'), None),
    (('N', None), False),
    (('N', 'P'), True),
    (('N', 'N'), False),
    (('N', 'NT'), None),
    (('NT', None), None),
    (('NT', 'P'), True),
    (('NT', 'N'), False),
    (('NT', 'NT'), None))


def test_check_pnt():
    """
    Ensure that we can properly report test results
    """
    for (code, confirm), expected in nat_tests:
        eq_(check_pnt(code, confirm), expected)


def test_result_check_dhbv():
    """
    Check that DHBV is properly registered
    """
    for (code, confirm), expected in nat_tests:
        result = Result(
            site_code='076C', reference_number='00000',
            nat=code, dhbv=confirm)
        value = result.check('dhbv')
        eq_(value, expected, '%s|%s = %s, got %s' % (
            code, confirm, expected, value))


def test_result_check_dhiv():
    """
    Check that DHIV is properly registered
    """
    for (code, confirm), expected in nat_tests:
        result = Result(
            site_code='076C', reference_number='00000',
            nat=code, dhiv=confirm)
        value = result.check('dhiv')
        eq_(value, expected, '%s|%s = %s, got %s' % (
            code, confirm, expected, value))


def test_result_check_dhcv():
    """
    Check that DHCV is properly registered
    """
    for (code, confirm), expected in nat_tests:
        result = Result(
            site_code='076C', reference_number='00000',
            nat=code, dhcv=confirm)
        value = result.check('dhcv')
        eq_(value, expected, '%s|%s = %s, got %s' % (
            code, confirm, expected, value))

def test_result_repr():
    """
    Checks if __repr__() function of Result provides correct value
    """

    for (code, confirm), expected in nat_tests:
        result = Result(
        site_code='076C', reference_number='00000',
        nat=code, dhcv=confirm)

        if code == None and confirm == None:
            test_repr_value = '<Result (reference_number=00000, site_code=076C)>'
        elif code == None:
            test_repr_value = '<Result (reference_number=00000, site_code=076C, dhcv=%s)>' % confirm
        elif confirm == None:
            test_repr_value = '<Result (reference_number=00000, site_code=076C, nat=%s)>' % code
        else:
            test_repr_value = '<Result (reference_number=00000, site_code=076C, nat=%s, dhcv=%s)>' % (code, confirm)

        actual_repr_value = result.__repr__()
        eq_(actual_repr_value, test_repr_value, '%s != %s' %(actual_repr_value, test_repr_value))

def test_draw_repr():
    """
    Checks if __repr__() function of Draw provides correct value
    """
    from datetime import datetime

    draw = Draw(site_code='076C', reference_number='00000', draw_date=datetime.strptime('2015-09-23', "%Y-%m-%d"))
    draw_date = str(datetime.strptime('2015-09-23', "%Y-%m-%d"))

    test_repr_value = '<Draw (draw_date=%s, reference_number=00000, site_code=076C)>' % draw_date

    actual_repr_value = draw.__repr__()
    eq_(actual_repr_value, test_repr_value, '%s != %s' %(actual_repr_value, test_repr_value))

@raises(NotImplementedError)
def test_result_check_unsuported():
    """
    Fail on unsupported test
    """
    result = Result(site_code='076C', reference_number='00000')
    result.check('foo')
