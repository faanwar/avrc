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

"""
Result data persistence
"""

from datetime import datetime

from sqlalchemy import (
    orm,
    Column, CheckConstraint, UniqueConstraint,
    Integer, Enum, Date, String, DECIMAL)
from sqlalchemy.ext import declarative

from avrc.redcross import __version__


Session = orm.scoped_session(orm.sessionmaker())

Base = declarative.declarative_base()


TYPES = frozenset(
    'hbs aby rpr hiv hbc ht1 hcv cmv nat wnv abo cgs dhiv dhcv dhbv'.split())


def check_pnt(code, confirm=None):
    """
    Verifies a nucleic test (P, N, NT) and (optionally) double checks against
    a confirmation test.

    For legacy reasons, the resulting value is consolidated to a boolean.
    Although in future versions this might be resolved to a character result.

    Parameters:
    code -- the test to to check against
    confirm -- (optional) double check code

    Returns:
        True if the code is not negative and the optional code is not negative.
    """
    if confirm is not None:
        if confirm == 'P':
            return True
        elif confirm == 'N':
            return False
    else:
        if code == 'N':
            return False


# How to calculate each test result
supported_tests = {
    'nat': lambda r: check_pnt(r.nat, r.nat),
    'dhbv': lambda r: check_pnt(r.nat, r.dhbv),
    'dhiv': lambda r: check_pnt(r.nat, r.dhiv),
    'dhcv': lambda r: check_pnt(r.nat, r.dhcv)
    }


# A nucleic acid test can yield only one of the following results
# This is poorly named as there is an ambiguously-named NAT test
# that is used for HIV...
NAT_RESULT_TYPES = ('N', 'P', 'NT')

BLOOD_TYPES = ('O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-')

NatEnum = Enum(*NAT_RESULT_TYPES, name='nat_result')


class Result(Base):
    """
    A Red Cross test result.

    This structure closely follows the file format we receive from the
    Red Cross via SFTP.

    Usually more normalization would be implemented, but due to the scope of
    this application, a simple table will suffice.
    """

    __tablename__ = 'result'

    id = Column(Integer, primary_key=True, autoincrement=True)

    site_code = Column(
        String(5), nullable=False, index=True,
        doc='Red Cross-assigned site code for the sample')

    reference_number = Column(
        String(8), nullable=False, index=True,
        doc='Instituion-specific subject reference number')

    # All the test result types the Red Cross can deliver
    # Currently we only receive HBV, HIV, HCV, and NAT
    hbs = Column(NatEnum)
    aby = Column(NatEnum)
    rpr = Column(NatEnum)
    hiv = Column(NatEnum)
    hbc = Column(NatEnum)
    ht1 = Column(NatEnum)
    hcv = Column(NatEnum)
    cmv = Column(NatEnum)
    nat = Column(NatEnum, nullable=False)
    wnv = Column(NatEnum)
    abo = Column(Enum(*BLOOD_TYPES, name='blood_type'))
    cgs = Column(NatEnum)
    dhiv = Column(NatEnum)
    dhcv = Column(NatEnum)
    dhbv = Column(NatEnum)
    nat_sco = Column(String) 
    dhiv_sco = Column(String) 
    dhbv_sco = Column(String) 
    dhcv_sco = Column(String) 

    test_date = Column(
        Date, nullable=False, default=datetime.today,
        doc='The date the test was return from the Red Cross')

    draw_date = Column(
        Date,
        CheckConstraint('draw_date IS NULL OR draw_date <= test_date'),
        doc='The date the sample was drawn from the clinic')

    location = Column(
        String(38),
        doc='The lab location this sample was drawn from')

    file = Column(
        String(32), default='None'
        doc='Which file the result was extracted from')

    version = Column(
        String(8), nullable=False, default=__version__,
        doc='The software version that generated this result')

    def check(self, type_):
        if type_ not in supported_tests:
            raise NotImplementedError(type_)
        return supported_tests[type_](self)

    __table_args__ = (
        UniqueConstraint(site_code, reference_number),)

    def __repr__(self):
        return '<%s (%s)>' % (
            self.__class__.__name__,
            ', '.join('%s=%s' % (k, v)
                      for k, v in self.__dict__.items()
                      if not k.startswith('_') and v is not None))

class Draw(Base):
    """
    Red cross identification numbers and their associated draw dates inputted by testers.
    This table is used to help the results.py page determine whether the user is able to view
    their testing results based on their draw dates.
    """

    __tablename__ = 'draw'

    id = Column(Integer, primary_key=True, autoincrement=True)

    site_code = Column(
        String(5), nullable=False, index=True,
        doc='Red Cross-assigned site code for the sample')

    reference_number = Column(
        String(8), nullable=False, index=True,
        doc='Instituion-specific subject reference number')

    draw_date = Column(
        Date, nullable=False,
        doc='The date the sample was drawn from the clinic')

    has_result = Column(
        Integer, nullable=False, index=True, default=0,
        doc='Integer value that indicates whether a corresponding Red Cross result has been found. "0" means false. "1" means true.')

    __table_args__ = (
        UniqueConstraint(site_code, reference_number),)

    def __repr__(self):
        return '<%s (%s)>' % (
            self.__class__.__name__,
            ', '.join('%s=%s' % (k, v)
                      for k, v in self.__dict__.items()
                      if not k.startswith('_') and v is not None))
