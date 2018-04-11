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
Utilities for parsing a Red Cross file
"""

import os
import platform
import re
import json
import traceback
import gnupg
from avrc.redcross import exc, log, models, Session 
import datetime
from redcapi import RCProject
import csv

def decrypt(infile, outfile, passphrase, home, binary=None):
    """
    GPG convenience wrapper to decrypt a file.

    Parameters:
    infile -- The encryped file name
    outfile -- The target decrypted file name
    passphrase -- The passphrase to decrypt the file with
    home -- GPG configuration directory (e.g. ~/.gnupg)
    binary -- (Optional) The custom gpg binary (default: 'gpg')
    """

    log.info('Decrypting %s' % infile)

    gpg = gnupg.GPG(gnupghome=home, gpgbinary=(binary or 'gpg'))

    with open(infile) as fp:
        status = gpg.decrypt_file(fp, passphrase=passphrase, output=outfile)

    if not status.ok:
        raise exc.ParserDecryptError(infile, status.stderr)

    log.info('Successfully decrypted')

def get_test_date(filename):
    """
    Try to get the date that a file was created, falling back to when it was
    last modified if that isn't possible.
    See http://stackoverflow.com/a/39501288/1709587 for explanation.
    """
    if platform.system() == 'Windows':
        return os.path.getctime(filename)
    else:
        stat = os.stat(filename)
        try:
            return stat.st_birthtime
        except AttributeError:
            # We're probably on Linux. No easy way to get creation dates here,
            # so we'll settle for when its content was last modified.
            return stat.st_mtime
 
def parse(file, settings):
    """
    Parses a Red Cross file.

    Parameters:
    file -- the file name of the Red Cross format file

    Returns:
    A list of un-persisted database entries extracted from the file.
    """
    with open(file) as fp:
        return parsefp(fp, settings)


def parsefp(fp, settings):
    """
    Parses a Red Cross file.

    Parameters:
    fp -- the file-like object to parse

    Returns:
    A list of un-persisted database entries extracted from the file.
    """
    results, duplicates = ([], [])

    try:
        name = os.path.basename(fp.name)
    except AttributeError:
        name = fp.__class__

    log.debug('Parsing %s' % name)
    expected = 0
    
    sites = settings.get('site.codes').split()
    rcs = json.loads(open(settings['redcap_json'],'r').read())

    redcap = RCProject(sites, rcs)

    readCSV = csv.reader(fp, delimiter=',')

    for i, line in readCSV:
        # The first line is the header, calculated expected rows
        if i == 0:
            expected = str2header(line)
            log.debug('Expecting %d lines' % expected)
            continue
        
        result = str2result(line)
        result.file = name

        exists = (
            Session.query(models.Result)
            .filter_by(site_code=result.site_code)
            .filter_by(reference_number=result.reference_number)
            .count())

        if exists:
            log.warn('(%d/%d) Duplicate %s %s' % (
                i, expected, result.site_code, result.reference_number))
            duplicates.append(result)
        else:
            log.debug(
                '(%d/%d) Extracted %s %s' % (
                    i, expected, result.site_code, result.reference_number))

            # Syncing draw dates
            rc_id = str(result.site_code) + str(result.reference_number)
            draw = redcap.project[result.site_code].export_records([rc_id], fields=['visit_date', 'test_site'], raw_or_label="label")	
	    
            # Ignore if this information is not available in the redcap db
            try:
              if draw[0]['visit_date'] != '':
                draw_date = datetime.datetime.strptime(draw[0]['visit_date'], "%Y-%m-%d").date()   
                result.draw_date = draw_date
            except:
		          pass
	      
            try:
              result.location = draw[0]['test_site']
            except:
              pass	

            results.append(result)

    processed = len(results) + len(duplicates)

    if processed != expected:
        raise exc.ParserIncompleteError(processed, expected)

    return results , duplicates


def str2header(string):
    """
    Parses a Red Cross header and extracts the total expected results.
    """
    match = re.search(r'(\d+)', string)
    if not match:
        raise exc.ParserHeaderError(string)
    return int(match.group(1))


def str2result(string):
    """
    Converts a string to a database result entry
    The result is not persisted and must be added to a database session.
    The locations within the string are considered "proprietary" by
    the Red Cross.
    """
    def clean(s):
        """ Helper method to sanitize the string """
        return s.strip() or None

    try:

        site_code = clean(string[0])
        reference_number = clean(string[1])

        result = models.Result(
            site_code=site_code,
            reference_number=reference_number,
            nat=clean(string[2]),
            nat_sco=clean(string[3]),
            dhiv=clean(string[4]),
            dhiv_sco=clean(string[5]),
            dhcv=clean(string[6]),
            dhcv_sco=clean(string[7]),
            dhbv=clean(string[8]),
            dhbv_sco=clean(string[9]))
        return result
    except:
        traceback.print_exc()
        raise exc.ParserValueError(string)

