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
Custom exceptions that can be raised by this package.
"""


class Error(Exception):
    """
    Base class for package exceptions.
    """


class ParserError(Error):
    """
    Base class for parser exceptions
    """


class ParserDecryptError(ParserError):
    """
    Raised when file decryption fails.
    """

    def __init__(self, file, stderr):
        self.file = file
        self.stderr = stderr
        self.msg = u'Unable to decrypt %s: %s' % (file, stderr)


class ParserHeaderError(ParserError):
    """
    Raised when the file header is malformed
    """

    def __init__(self, header):
        self.header = header
        self.msg = u'No row count found in header: %s' % self.header


class ParserValueError(ParserError):
    """
    Raised when unable to parse a strint to a result object.
    """

    def __init__(self, value):
        self.value = value
        self.msg = u'Attempted to parse invalid value: "%s"' % self.value


class ParserIncompleteError(ParserError):
    """
    Raised when the parser completes with a different total than the one
    declarared by the header row.
    """

    def __init__(self, got, expected):
        self.got = got
        self.expected = expected
        self.msg = u'Expected %d lines, got %d' % (self.expected, self.got)


class NoRecordFound(Exception):
    """
    Raised when no record was found by the REST service
    """


class MultipleRecordsFound(Exception):
    """
    Raised when multiple records were found by the REST service
    """

class RedCAPTokenExpired(Exception):
    def __init__(self, date):
	self.date = date
	self.msg = u'The RedCAP API has expired on %s. Please visit http://redcap.ucsd.edu to renew' % (self.date)

