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

from avrc.redcross.models import Base, Result, Draw # flake8: noqa
from pyramid.security import Allow, ALL_PERMISSIONS

ou = ',ou=earlytest,ou=groups,dc=cfar,dc=edu'
members_cn = 'cn=earlytest-members' + ou
admins_cn  = 'cn=earlytest-admins'  + ou
avrc_cn    = 'cn=earlytest-avrc'    + ou
oakland_cn = 'cn=earlytest-oakland' + ou
emory_cn   = 'cn=earlytest-emory'   + ou
data_cn    = 'cn=earlytest-data'    + ou

class RootFactory(object):
  __acl__ = \
  [
    (Allow, admins_cn, ALL_PERMISSIONS),
    (Allow, avrc_cn, ['avrc', 'reports', 'draw-input']),
    (Allow, oakland_cn, ['oakland', 'reports', 'draw-input']),
    (Allow, emory_cn, ['emory', 'reports', 'draw-input']),
    (Allow, data_cn, ['draw-input']),
  ]
  def __init__(self, request):
    pass

def nonecmp(a,b):
    if a is None and b is None:
        return 0
    if a is None:
        return -1
    if b is None:
        return 1
    return cmp(a,b)
