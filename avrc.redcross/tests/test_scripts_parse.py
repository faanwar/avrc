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
try:
    import configparser
except ImportError:
    import ConfigParser as configparser
import os.path
import re
import shutil
import sys
import tempfile

import gnupg
from nose.tools import eq_
import turbomail
import transaction
import datetime

from avrc.redcross import scripts, Session, models


class TestMain(object):

    def setup(self):
        Session.remove()
        self.tempdir = tempfile.mkdtemp()
        self.configfile = os.path.join(self.tempdir, 'config')
        self.datafile = os.path.join(self.tempdir, 'data')
        self.homedir = tempfile.mkdtemp(dir=self.tempdir)

        config = configparser.SafeConfigParser()
        config.add_section('settings')
        config.set('settings', 'dir.raw', os.path.join(self.tempdir, 'raw'))
        config.set('settings', 'dir.web', os.path.join(self.tempdir, 'web'))
        config.set('settings', 'sqlalchemy.url',
                   'sqlite:///' + os.path.join(self.tempdir, 'db'))
        config.set('settings', 'gpg.home', self.homedir)
        config.set('settings', 'gpg.passphrase', 'secret')
        config.set('settings', 'gpg.binary', 'gpg')
        config.set('settings', 'mail.on', 'True')
        config.set('settings', 'mail.message.author', 'proc@localhost')
        config.set('settings', 'notify.error', 'foo@localhost')
        config.set('settings', 'notify.999X.dhiv', 'foo@localhost')
        config.set('settings', 'notify.999X.dhcv', 'foo@localhost')
        config.set('settings', 'notify.999X.dhbv', 'foo@localhost')
        config.set('settings', 'notify.diagnostic', 'foo@localhost')

        self.config = config

        with open(self.configfile, 'w+') as fp:
            config.write(fp)

        sys.argv = ['', '-c', self.configfile]
        scripts.initdb.main()

        self.passphrase = 'secret',

        gpg = gnupg.GPG(gnupghome=self.homedir)
        self.gpg = gpg

        # persist the keys so the function properly reload them
        with tempfile.NamedTemporaryFile(dir=self.homedir) as fp:
            key = gpg.gen_key(gpg.gen_key_input())
            fp.write(gpg.export_keys(str(key)))
            fp.write(gpg.export_keys(str(key), True))

        self.key = key

        # The database will be reconfigured with the commannd, so make sure
        # it is not bound to a database
        Session.remove()

    def teardown(self):
        # reset the temporary directory to system default
        shutil.rmtree(self.tempdir)
        turbomail.interface.stop(force=True)
        turbomail.interface.config = {'mail.on': False}
        Session.remove()

    def test_error(self):
        """
        Ensure developers get notified of problems with the parsing.
        This is an automated process so it's useful to ping developers if
        something unexpectedly goes wrong.
        """
        config = self.config
        datafile = os.path.join(self.tempdir, 'data')

        # Intentionally screw something up
        config.remove_option('settings', 'gpg.home')

        with open(self.configfile, 'w+') as fp:
            config.write(fp)

        try:
            sys.argv = ['', '-c', self.configfile, datafile]
            scripts.parse.main()
        except:
            # the command will re-raise the exception, suppress it so we
            # can read the email
            pass

        emails = turbomail.interface.manager.transport.get_sent_mails()
        eq_(1, len(emails))
        email_content = emails.pop()
        assert 'Traceback' in email_content

    def test_main(self):
        gpg = self.gpg
        datafile = os.path.join(self.tempdir, 'data')

        io = StringIO()
        print >>io, 'Has 1 result'
        print >>io, '076CX 12345                                     P'
        io.flush()
        io.seek(0)
        gpg.encrypt_file(
            io, str(self.key), passphrase=self.passphrase, output=datafile)
        io.close()

        sys.argv = ['', '-c', self.configfile, datafile]
        scripts.parse.main()

        eq_(1, Session.query(models.Result).count())

    def test_duplicate(self):
        """
        Ensure we get notified if a duplicate entry is attempted
        """
        gpg = self.gpg
        datafile = os.path.join(self.tempdir, 'data')

        io = StringIO()
        print >>io, 'Has 1 result'
        print >>io, '076C 12345                                      P'
        io.flush()
        io.seek(0)
        gpg.encrypt_file(
            io, str(self.key), passphrase=self.passphrase, output=datafile)
        io.close()

        sys.argv = ['', '-c', self.configfile, datafile]
        scripts.parse.main()
        Session.remove()

        io = StringIO()
        print >>io, 'Has 1 result'
        print >>io, '076C 12345                                      N'
        io.flush()
        io.seek(0)
        gpg.encrypt_file(
            io, str(self.key), passphrase=self.passphrase, output=datafile)
        io.close()

        try:
            sys.argv = ['', '-c', self.configfile, datafile]
            scripts.parse.main()
            Session.remove()
        except:
            # the command will re-raise the exception, suppress it so we
            # can read the email
            pass

        emails = turbomail.interface.manager.transport.get_sent_mails()
        eq_(1, len(emails))
        email_content = emails.pop()
        expected = 'Already exists: 76C12345'
        assert expected in email_content

    def test_dry(self):
        """
        Ensure --dry option doesn't affect the file system and database
        """
        config = self.config
        gpg = self.gpg
        datafile = os.path.join(self.tempdir, 'data')

        io = StringIO()
        print >>io, 'Has 1 result'
        print >>io, '076C 12345                                      P'
        io.flush()
        io.seek(0)
        gpg.encrypt_file(
            io, str(self.key), passphrase=self.passphrase, output=datafile)
        io.close()

        sys.argv = ['', '-c', self.configfile, '--dry', datafile]
        scripts.parse.main()

        eq_(0, Session.query(models.Result).count())
        assert not os.path.exists(
            os.path.join(config.get('settings', 'dir.web'), '76C.html'))
        assert not os.path.exists(
            os.path.join(config.get('settings', 'dir.web'), '76C.xls'))

    def test_notify_positive(self):
        """
        Ensure interested parties get the positive test notifications
        """
        gpg = self.gpg
        datafile = os.path.join(self.tempdir, 'data')

        io = StringIO()
        print >>io, 'Has 1 result'
        #                      1         2         3         4         5         6         7            # NOQA
        #            01234567890123456789012345678901234567890123456789012345678901234567890123456789   # NOQA
        print >>io, '999X 12345                                      P               P  N  N'           # NOQA
        io.flush()
        io.seek(0)
        gpg.encrypt_file(
            io, str(self.key), passphrase=self.passphrase, output=datafile)
        io.close()

        sys.argv = ['', '-c', self.configfile, datafile]
        scripts.parse.main()

        emails = turbomail.interface.manager.transport.get_sent_mails()
        # 2 Emails sent. One for HIV. One for missing draw dates.
        eq_(2, len(emails))
        email_content = emails[0]
        assert 'result updates' in email_content
        assert 'DHIV' in email_content
        assert '999X' in email_content
        assert re.search('Positive:\s+1', email_content)

    def test_notify_not_tested(self):
        """
        Ensure interested parties get the not tested test notifications
        """
        gpg = self.gpg
        datafile = os.path.join(self.tempdir, 'data')

        io = StringIO()
        print >>io, 'Has 1 result'
        #                      1         2         3         4         5         6         7            # NOQA
        #            01234567890123456789012345678901234567890123456789012345678901234567890123456789   # NOQA
        print >>io, '999X 12345                                      P              NT  N  N'           # NOQA
        io.flush()
        io.seek(0)
        gpg.encrypt_file(
            io, str(self.key), passphrase=self.passphrase, output=datafile)
        io.close()

        sys.argv = ['', '-c', self.configfile, datafile]
        scripts.parse.main()

        emails = turbomail.interface.manager.transport.get_sent_mails()
        # 2 Emails sent. One for HIV. One for missing draw dates.
        eq_(2, len(emails))
        email_content = emails[0]
        assert 'result updates' in email_content
        assert 'DHIV' in email_content
        assert '999X' in email_content
        assert re.search('Other:\s+1', email_content)

    def test_ignore_negatives(self):
        """
        Do not send emails for negative results.
        """
        gpg = self.gpg
        datafile = os.path.join(self.tempdir, 'data')

        io = StringIO()
        print >>io, 'Has 1 result'
        print >>io, '999X 12345                                      P               N  N  N'  # NOQA
        io.flush()
        io.seek(0)
        gpg.encrypt_file(
            io, str(self.key), passphrase=self.passphrase, output=datafile)
        io.close()

        sys.argv = ['', '-c', self.configfile, datafile]
        scripts.parse.main()


        emails = turbomail.interface.manager.transport.get_sent_mails()
        # Only one email should have been sent for missing draw results
        eq_(1, len(emails))
        email_content = emails[0]
        assert 'AEH-Redcross update' in email_content
        assert 'matching draw date' in email_content
        assert 'not entered' in email_content
        assert re.search('received\s+1', email_content)


    def test_notify_missing_draw_dates(self):
        """
        Ensure interested parties get missing draw date notifications
        """
        gpg = self.gpg
        datafile = os.path.join(self.tempdir, 'data')

        io = StringIO()
        print >>io, 'Has 1 result'
        #                      1         2         3         4         5         6         7            # NOQA
        #            01234567890123456789012345678901234567890123456789012345678901234567890123456789   # NOQA
        print >>io, '999X 12345                                      P               N  N  N'           # NOQA
        io.flush()
        io.seek(0)
        gpg.encrypt_file(
            io, str(self.key), passphrase=self.passphrase, output=datafile)
        io.close()

        sys.argv = ['', '-c', self.configfile, datafile]
        scripts.parse.main()

        emails = turbomail.interface.manager.transport.get_sent_mails()
        # Only one email should have been sent for missing draw results
        eq_(1, len(emails))
        email_content = emails[0]
        assert 'AEH-Redcross update' in email_content
        assert 'matching draw date' in email_content
        assert 'not entered' in email_content
        assert re.search('received\s+1', email_content)

    def test_FindMissingDraw_AllResultsLessThan6MonthsOldAndAllMissingDrawDates_ReturnListOfAllResults(self):
        """
        Should return 5 (all) results in a list. These results are missing draw dates and
        their test dates are less than 180 days old.
        """


        missing_draw = []
        current_time = datetime.date.today()
        date1 = current_time - datetime.timedelta(days=30)
        date2 = current_time - datetime.timedelta(days=60)
        date3 = current_time - datetime.timedelta(days=90)
        date4 = current_time - datetime.timedelta(days=120)
        date5 = current_time - datetime.timedelta(days=150)

        # Add 5 unique results where 5 results are missing their draw date and
        # 5 are less than 6 months old
        site_code = '99X'
        reference_number1 = '11111'
        reference_number2 = '22222'
        reference_number3 = '33333'
        reference_number4 = '44444'
        reference_number5 = '55555'


        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number1,
                test_date=date1,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number2,
                test_date=date2,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number3,
                test_date=date3,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number4,
                test_date=date4,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number5,
                test_date=date5,
                nat='P',
                dhiv='N',
                file='results.txt'))

        transaction.commit()

        missing_draw = scripts.parse.find_missing_draw()

        # Correct number of missing draw date cases?
        assert len(missing_draw) == 5

        # Are they really missing draw dates?
        for x in missing_draw:
            assert not x.draw_date

        results_expiration = current_time - datetime.timedelta(days=180)

        # Are their test dates under 180 days
        for x in missing_draw:
            assert x.test_date > results_expiration

    def test_FindMissingDraw_AllResultsMoreThan6MonthsOldAndAllMissingDrawDates_ReturnEmptyListOfResults(self):
        """
        Should return an empty list of results because all results' test date is older
        than 180 days. All results are missing draw dates.
        """


        missing_draw = []

        current_time = datetime.date.today()
        date1 = current_time - datetime.timedelta(days=190)
        date2 = current_time - datetime.timedelta(days=200)
        date3 = current_time - datetime.timedelta(days=250)
        date4 = current_time - datetime.timedelta(days=300)
        date5 = current_time - datetime.timedelta(days=350)

        # Add 5 unique results where 5 results are missing their draw date and
        # 5 are more than 6 months old
        site_code = '99X'
        reference_number1 = '11111'
        reference_number2 = '22222'
        reference_number3 = '33333'
        reference_number4 = '44444'
        reference_number5 = '55555'


        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number1,
                test_date=date1,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number2,
                test_date=date2,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number3,
                test_date=date3,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number4,
                test_date=date4,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number5,
                test_date=date5,
                nat='P',
                dhiv='N',
                file='results.txt'))

        transaction.commit()

        missing_draw = scripts.parse.find_missing_draw()

        # Correct number of missing draw date cases?
        assert len(missing_draw) == 0

    def test_FindMissingDraw_MixedResultsMoreAndLessThan6MonthsOldAndAllMissingDrawDates_ReturnListOfValidResults(self):
        """
        Should return 3 results out of 5 in a list. These 3 results' test date are less
        than 180 days. All results are missing draw dates.
        """


        missing_draw = []
        current_time = datetime.date.today()
        date1 = current_time - datetime.timedelta(days=30)
        date2 = current_time - datetime.timedelta(days=60)
        date3 = current_time - datetime.timedelta(days=90)
        # Older than 180 days
        date4 = current_time - datetime.timedelta(days=200)
        date5 = current_time - datetime.timedelta(days=300)

        # Add 5 unique results where 5 results are missing their draw date and
        # 3 are less than 6 months old. The other 2 are more than 6 months old.
        site_code = '99X'
        reference_number1 = '11111'
        reference_number2 = '22222'
        reference_number3 = '33333'
        reference_number4 = '44444'
        reference_number5 = '55555'


        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number1,
                test_date=date1,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number2,
                test_date=date2,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number3,
                test_date=date3,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number4,
                test_date=date4,
                nat='P',
                dhiv='N',
                file='results.txt'))

        Session.add(
            models.Result(
                site_code=site_code,
                reference_number=reference_number5,
                test_date=date5,
                nat='P',
                dhiv='N',
                file='results.txt'))

        transaction.commit()

        missing_draw = scripts.parse.find_missing_draw()

        # Correct number of missing draw date cases?
        assert len(missing_draw) == 3

        # Are they really missing draw dates?
        for x in missing_draw:
            assert not x.draw_date

        results_expiration = current_time - datetime.timedelta(days=180)

        # Are their test dates under 180 days
        for x in missing_draw:
            assert x.test_date > results_expiration


    def test_DrawDateSync_ResultHasCorrespondingDrawDateInDrawTable_ResultDrawDateIsSynced(self):
        """
        Should sync draw dates from Draw table to results in Result table
        """

        # Add draw date to draw table first
        site_code = '999X'
        reference_number = '12345'

        # Add draw date to Draw table
        Session.add(
            models.Draw(
                site_code=site_code,
                reference_number=reference_number,
                draw_date=datetime.date.today())
        )
        transaction.commit()

        gpg = self.gpg
        datafile = os.path.join(self.tempdir, 'data')

        io = StringIO()
        print >>io, 'Has 1 result'
        print >>io, '999X 12345                                      P               N  N  N'  # NOQA
        io.flush()
        io.seek(0)
        gpg.encrypt_file(
            io, str(self.key), passphrase=self.passphrase, output=datafile)
        io.close()

        sys.argv = ['', '-c', self.configfile, datafile]
        scripts.parse.main()

        result = Session.query(models.Result)\
            .filter(models.Result.site_code == site_code)\
            .filter(models.Result.reference_number == reference_number).first()

        # Is there a draw date?
        assert result.draw_date

    def test_DrawDateSync_ResultHasNoCorrespondingDrawDateInDrawTable_ResultDrawDateIsNone(self):
        """
        Result draw dates should be None if no available corresponding draw date in Draw table
        Sync code is in parser.py
        """

        site_code = '999X'
        reference_number = '12345'

        gpg = self.gpg
        datafile = os.path.join(self.tempdir, 'data')

        io = StringIO()
        print >>io, 'Has 1 result'
        print >>io, '999X 12345                                      P               N  N  N'  # NOQA
        io.flush()
        io.seek(0)
        gpg.encrypt_file(
            io, str(self.key), passphrase=self.passphrase, output=datafile)
        io.close()

        sys.argv = ['', '-c', self.configfile, datafile]
        scripts.parse.main()

        result = Session.query(models.Result)\
            .filter(models.Result.site_code == site_code)\
            .filter(models.Result.reference_number == reference_number).first()

        # Is there a draw date?
        assert not result.draw_date
