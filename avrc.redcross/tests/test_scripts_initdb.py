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

try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import os.path
import shutil
import sys
import tempfile

from nose.tools import with_setup
from sqlalchemy import create_engine

from avrc.redcross import scripts, Session


def setup_func():
    # create temporary temporary directory that can be referenced
    tempfile.tempdir = tempfile.mkdtemp()


def teardown_func():
    # reset the temporary directory to system default
    shutil.rmtree(tempfile.tempdir)
    tempfile.tempdir = None

    # also remove any sessions created by the config file
    Session.remove()


@with_setup(setup_func, teardown_func)
def test_main():
    """
    Ensure resources can be properly initialized
    """
    tempdir = tempfile.tempdir

    config = configparser.SafeConfigParser()
    config.add_section('settings')
    config.set('settings', 'dir.test', os.path.join(tempdir, 'test'))
    config.set('settings', 'sqlalchemy.url', 'sqlite:///' + os.path.join(tempdir, 'db'))

    with tempfile.NamedTemporaryFile('wb+') as fp:
        config.write(fp)
        fp.flush()

        sys.argv = ['', '-c', fp.name]
        scripts.initdb.main()

        assert os.path.isdir(config.get('settings', 'dir.test'))

        engine = create_engine(config.get('settings', 'sqlalchemy.url'))
        assert 'result' in engine.table_names()
