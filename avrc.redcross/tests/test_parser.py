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

from cStringIO import StringIO
import os.path
import tempfile
import shutil

import gnupg

from nose.tools import raises, eq_, assert_raises
from sqlalchemy import create_engine

from avrc.redcross import models, Session, parser, exc


def setup_module():
    engine = create_engine('sqlite://')
    models.Base.metadata.create_all(bind=engine)
    Session.configure(bind=engine)


def teardown_module():
    Session.remove()


def teardown():
    Session.rollback()


@raises(exc.ParserHeaderError)
def test_str2header_invalid():
    parser.str2header('Has no integer')


def test_str2header_valid():
    eq_(parser.str2header('This file has 5 lines!'), 5)


def test_str2result_sample():
    value = '1234 67890123456'
    eq_(parser.str2result(value).site_code, '1234')
    eq_(parser.str2result(value).reference_number, '67890')


def test_ucsd_sample():
    value = '076C 12345'
    eq_(parser.str2result(value).site_code, '76C')
    eq_(parser.str2result(value).reference_number, '12345')


def test_oakland_east_bay_sample():
    value = '076GH12345'
    eq_(parser.str2result(value).site_code, '76GH')
    eq_(parser.str2result(value).reference_number, '12345')


def test_str2result():

    def assert_nucleic(start, prop):
        """Helper method to assert all possible test results"""
        fill = 'XXXX YYYYY'.ljust(start)
        for value in ('P', 'N', 'NT'):
            result = parser.str2result(fill + value)
            eq_(getattr(result, prop), value)

    def assert_blood(start, prop):
        """ Helper method to assert blood test result"""
        fill = 'XXXX YYYYY'.ljust(start)
        for value in ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'):
            result = parser.str2result(fill + value)
            eq_(getattr(result, prop), value)

    assert_nucleic(18, 'hbs')
    assert_nucleic(21, 'aby')
    assert_nucleic(24, 'rpr')
    assert_nucleic(27, 'hiv')
    assert_nucleic(30, 'hbc')
    assert_nucleic(33, 'ht1')
    assert_nucleic(36, 'hcv')
    assert_nucleic(42, 'cmv')
    assert_nucleic(48, 'nat')
    assert_nucleic(51, 'wnv')
    assert_blood(55, 'abo')
    assert_nucleic(60, 'cgs')
    assert_nucleic(63, 'dhiv')
    assert_nucleic(66, 'dhcv')
    assert_nucleic(69, 'dhbv')


def test_str2result_no_zerofill():
    """
    Ensure zeros are striped from the start of the site code.

    The Red Cross sends zero-filled site codes but every form of
    reference at the AVRC from papers/bar codes/index cards does
    not use the zeros and so including them into the database
    would destroy the workflow ecosystem.
    """
    value = '0099G12345'
    result = parser.str2result(value)
    eq_(result.site_code, '99G')


@raises(exc.ParserValueError)
def test_str2result_invalid():
    parser.str2result(None)


def test_parse_open():
    """
    Makde sure we can open the file and pass it to ``parsefp``
    """
    with tempfile.NamedTemporaryFile() as fp:
        results, duplicates = parser.parse(fp.name)
    eq_(len(results), 0)
    eq_(len(duplicates), 0)


def test_parsfp_empty():
    fp = StringIO()
    results, duplicates = parser.parsefp(fp)
    fp.seek(0)
    eq_(len(results), 0)
    eq_(len(duplicates), 0)


def test_parsefp_empty_decl():
    fp = StringIO()
    print >>fp, 'Line 0'
    fp.seek(0)
    results, duplicates = parser.parsefp(fp)
    eq_(len(results), 0)
    eq_(len(duplicates), 0)


@raises(exc.ParserIncompleteError)
def test_parsefp_bad_decl():
    fp = StringIO()
    print >>fp, 'Line 1'
    fp.seek(0)
    results, duplicates = parser.parsefp(fp)


def test_parsefp_good_result():
    fp = StringIO()
    print >>fp, 'Line 1'
    print >>fp, 'XXXX YYYYY'.ljust(80)
    fp.seek(0)
    results, duplicates = parser.parsefp(fp)
    eq_(len(results), 1)
    eq_(len(duplicates), 0)


def test_parsefp_duplicate_result():
    """
    Ensure we can detect duplicates
    """
    site_code = 'XXXX'
    reference_number = 'YYYYY'

    # Create a pre-existing result
    Session.add(models.Result(
        site_code=site_code, reference_number=reference_number, nat='N',
        file='oldfile.txt'))
    Session.flush()

    fp = StringIO()
    print >>fp, 'Line 1'
    print >>fp, (site_code + ' ' + reference_number).ljust(80)
    fp.seek(0)
    results, duplicates = parser.parsefp(fp)
    eq_(len(results), 0)
    eq_(len(duplicates), 1)


class TestDecrypt(object):
    """
    Test GPG decryption.
    """

    def setup(self):
        self.homedir = tempfile.mkdtemp()
        self.otherdir = tempfile.mkdtemp()

        # encrypt_file/decrypt_file delete the ouput file before using it
        # workaround is to use filenames inside the tempdir
        # http://code.google.com/p/python-gnupg/issues/detail?id=85
        self.encfile = os.path.join(self.homedir, 'enc')
        self.decfile = os.path.join(self.homedir, 'dec')
        self.message = 'Hide me!'
        self.passphrase = 'secret',

        gpg = gnupg.GPG(gnupghome=self.homedir)

        # persist the keys so the function properly reload them
        with tempfile.NamedTemporaryFile(dir=self.homedir) as fp:
            key = gpg.gen_key(gpg.gen_key_input())
            fp.write(gpg.export_keys(str(key)))
            fp.write(gpg.export_keys(str(key), True))

        # python gpg api is rather clunky,
        # needs input file stream, but output file name...
        io = StringIO(self.message)
        gpg.encrypt_file(
            io, str(key), passphrase=self.passphrase, output=self.encfile)
        io.close()

    def teardown(self):
        shutil.rmtree(self.homedir)

    def test_success(self):
        parser.decrypt(
            self.encfile, self.decfile, self.passphrase, home=self.homedir)

        with open(self.decfile) as fp:
            decrypted = fp.read()

        eq_(decrypted, self.message)

    def test_fail(self):
        assert_raises(
            exc.ParserDecryptError,
            parser.decrypt,
            self.encfile, self.decfile, 'evil', home=self.otherdir)
