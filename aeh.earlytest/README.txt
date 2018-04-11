..
   This software is Copyright (c) 2015,
   The Regents of the University of California.

   Developed by the UCSD CFAR BIT Core (bitcore@ucsd.edu)

   Core Developers:
     Sergei L Kosakovsky Pond (spond@ucsd.edu)
     Jason A Young (jay007@ucsd.edu)
     Marco A Martinez (mam002@ucsd.edu)
     Steven Weaver (sweaver@ucsd.edu)

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


Red Cross Web Site and Result Retrieval Application
===================================================

This package implements the web application for The Early Test program. The primary purpose of this application is to be a website with information about the program as well as a place for patients to retrieve their HIV test result. Additionally, it allows designated staff to view a comprehensive list of past HIV results for auditing purposes. The draw date input page was recently added to this application. Staff can now enter the draw date and Red Cross ID for each earlytest. The application depends on the draw date to determine when the client may retrieve their HIV test result. The application is using the pyramid web development framework.

The results component should adhere to the to following guidelines set up
by the Early Test protocol:

* Only disclose HIV negative results to a patient with a proper
  identification number.
* Only disclose HIV negative result 2 (two) weeks after the original
  test date.
* Disable HIV test result retrieval after a period of three (3) months
  after the original test date.

The reports component should only allowed designated staff via LDAP
to authenticate and view results.

