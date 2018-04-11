..
   This software is Copyright (c) 2015,
   The Regents of the University of California.

   Developed by the UCSD CFAR BIT Core (bitcore@ucsd.edu)

   Core Developers:
     Sergei L Kosakovsky Pond (spond@ucsd.edu)
     Jason A Young (jay007@ucsd.edu)
     Marco A Martinez (mam002@ucsd.edu)
     Steven Weaver (sweaver@ucsd.edu)
     Zachary Smith (z4smith@ucsd.edu)

   Significant contributions from:
     David Mote (davidmote [at] gmail [dot] com)
     Jennifer Rodriguez-Mueller (almostlikethat [at] gmail [dot] com)
     Drew Allen (asallen@ucsd.edu)
     Andrew Dang (a7dang [at] gmail [dot] com)

   Redistribution and use in source and binary forms, with or without
   modification, are permitted provided that the following conditions are met:

   * Redistributions of source code must retain the above copyright notice, this
     list of conditions and the following disclaimer.

   * Redistributions in binary form must reproduce the above copyright notice,
     this list of conditions and the following disclaimer in the documentation
     and/or other materials provided with the distribution.

   THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
   AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
   IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
   ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
   LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
   CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
   SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
   INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
   CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
   ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
   POSSIBILITY OF SUCH DAMAGE.


Red Cross Test Result Processing Pipeline
=========================================

This package implements commands to keep track of Red Cross test result data and draw dates. Recently, the OCCAMS system has been removed. OCCAMS was a database the AVRC was using before the switch over to Red Cap. OCCAMS stored client research profiles which were updated with the Red Cross test result data from this pipeline twice a day. OCCAMS also synchronized the local Result table with draw dates to be used by the aeh.earlytest package. As mentioned, the draw date input page was added to update the Result table with draw dates. The Red Cross is sent a request to perform Nucleic Acid Tests (i.e. NAT) and will deliver the results in PGP-encrypted file via SFTP. Note that NAT can be a confusing acronym as it’s used by the personnel of the AVRC to reference the specific test for HIV status. Furthermore, the Red Cross name for this test is also NAT, even though there can be other nucleic acid tests for other infections (e.g. a nat test for west nile virus.


Overview
--------

This package is part of a web of components necessary for disclosing a patient with their Red Cross HIV test Result. This particular package’s responsibilities are to process and store encrypted Red Cross result files in a local database. Every time the parse script is run, it checks the Draw table in the same sqlite database as the Result table for a corresponding draw date. It then updates the result with the draw date. The way the data is used after this, is entirely up to the standard operating procedures setup with the institution using these scripts. For example, the AVRC protocol stipulates that the result not be disclosed to the patient until after 2 (two) weeks after the test date, but not 3 (three) months and only if they are HIV negative.**.



System Requirements
-------------------

* Python 2.6+
* sqlite
* xmllib2
* xsltlib2
* rng-tools (if you're going to run the unit tests)
* gnupg with PGP enabled (in most cases you'll have to compile this yourself
  as most Linux flavors don't support it).


Installation
------------

This installation assumes you are familiar with the ``virtualenv`` Python utility.

Set up the environment you'll be running the package with::

  $ virtualenv DEST
  $ cd DEST
  $ source ./bin/activate
  $ git clone git@bitbucket.org:ucsdbitcore/avrc.redcross.git
  $ pip install -e ./avrc.redcross



Using the commands
------------------

The package will install scripts into the environment's ``bin`` directory.
Below is a description of what each of the commands does, for more information
on how to use each command, run the command with ``--help``:

================  ============================================================
Command           Description
================  ============================================================
``rc_initdb``     Sets up directories and local database for storing the
                  results

``rc_parse``      Parses an encrypted red cross file.

================  ============================================================


Configuration
-------------

Edit the configurations as necessary (a sample is included for you, see below
for further notes on what the parameters do)::

  $ cp ./avrc.redcross/settings-sample.ini ./settings.ini
  $ vim ./settings.ini

Documentation on how to edit configurations for python:
https://docs.python.org/2/library/configparser.html


Parameters
+++++++++++++++++++++++

======================= ======================================================
Setting                 Description
======================= ======================================================
``dir.raw``             Where to store encrypted files after they've been
                        processed.

``sqlalchemy.url``      Database binding URL

``gpg.binary``          Path to GPG binary.

``gpg.home``            The home directory of the effective user

``gpg.passphrase``      The passphrase that is setup with the data file
                        encryption.

``mail.on``             Enables/Disables email notifications. Useful for
                        turning off while troubleshooting.
                        This is part of turbomail's settings:
                        http://pythonhosted.org/TurboMail/chapters/using.html#configuration-options

``mail.transport``      Mail transport to use (e.g. smtp

``mail.smtp.server``    The SMTP server hostname

``mail.message.author`` The author to use when sending out emails.

``notify.error``        List of emails to notify in the event of a runtime
                        error

``notify.diagnostic``   List of emails to notify with debug messages

``notify.SITE.TEST``    List of emails to notify about a POSTIVE result for
                        a particular site. For example `notify.0123X.dhiv`
                        will notify the listed emails of HIV positive results
                        for the 0123X site. The list of available test results
                        are:

                        * ``nat``
                        * ``dhbv``
                        * ``dhiv``
                        * ``dhcv``

======================= ======================================================


Testing
-------

Before you begin testing, you **MUST** install `rng-tools`, this is so that
the tests can generate enough entropy during (R)andom (N)umber (G)eneration
for proper PGP encryption so that we can test the decryption process.

Use your system's preffered way of installing libraries, for example on
CentOS::

  $ sudo yum install rng-tools

Once the libraries are installed, ensure that they are activated, for example,
on CentOS::

  $ sudo service rngd start

**NOTE**: On CentOS systems, you may receive this error message when you run the
above command:

  Starting rngd: can't open entropy source(tpm or intel/amd rng)
  Maybe RNG device modules are not loaded

This means that you may need to edit `/etc/sysconfig/rngd` and add the
following option::

  EXTRAOPTIONS="-r /dev/urandom"

Now that you have property RNG entropy, install the testing libraries in your
environment as follows::

  $ pip install -e ./avrc.redcross[test]

The above commands will install additional tools for you to run the tests::

  $ cd PKG_PATH
  $ nosetests
