## This software is Copyright (c) 2017,
## The Regents of the University of California.
##
##
## Core Developers:
##   Ajay Mohan (ajmohan [at] ucsd [dot] edu)
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##
## * Redistributions of source code must retain the above copyright notice, this
##   list of conditions and the following disclaimer.
##
## * Redistributions in binary form must reproduce the above copyright notice,
##   this list of conditions and the following disclaimer in the documentation
##   and/or other materials provided with the distribution.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
## AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
## IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
## ARE DISCLAIMED.  IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE
## LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
## CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF
## SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS
## INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN
## CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
## ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
## POSSIBILITY OF SUCH DAMAGE.

## Email Body
### -*- coding: utf-8 -*-
<html>
<head>
  <title> Early Test Reminder </title>
</head>
<body>
<table width="100%" border="0" cellspacing="100%" cellpadding="0" padding="10px">
  <tr>
    <td>
      <br>
      Dear <b>${username}</b>,
    </td>
  </tr>
  <tr>
    <td align="left">
    <br>
        According to our records, 3 months is approaching (or has already passed) since you last tested with us at UCSD's AntiViral Research Center (AVRC) HQ (using the email  ${email}). Do you think this might be a good time to schedule your next test? Our testing schedule is once every 3 months; due to funding limitations, we are unable to test people more frequently.     </td>
  </tr>
  <tr>
    <td>
    <br>
    For those that qualify, (men who have sex with men, and/or trans females), we offer the Total Test at our Good To Go (AVRC UP) location. The Total Test bundle includes STD screening (syphilis, gonorrhea, chlamydia) and immediate PrEP. We still offer the Early Test at other locations (see below). </td>
  </tr>
  <tr>
    <td>
    <br/>
    From our standpoint, you are 'Good To Go' when you know your status(es), are treated for STDs, on PrEP and have a sexual health plan in place. If that's all good, you're good to go, and you can get right back to getting busy! 
    </td>
  </tr>
  <tr>
    <td>
    <br>
 
       <table width="100%" border="0" cellspacing="100%" cellpadding="0" padding="10px">
       <tr><b>HIV / STD / PrEP (Total Test) </b></tr>
       <tr>
          <td>
          <br>
            AVRC University & Park (UP): <br/>
            www.goodtogosd.com <br/>
            619-543-9340 <br/>
            3830 Park Boulevard, San Diego, CA 92103 <br/>
            (Corner of University Avenue and Park Boulevard)</br>
            Monday - Friday: Noon - 8:00pm <br/>
            Saturday: 10:00am - 4:00pm <br/>

          </td>
        </tr>

       <br />

        <tr>
          <td>
          <br>
            <b>HIV Testing Only (Early Test)</b> <br/>
            AVRC Headquarters (HQ): <br/>
            619-543-8080 <br/>
            220 Dickinson Street, Suite A, San Diego, CA 92103. <br/>
            Monday - Thursday: 09:00am - 3:00pm, <br/>
            Friday: 09:00am - noon <br/>

          </td>
        </tr>
        <tr>
          <td>
          <br>
            The San Diego LGBT Community Center:<br /> 619-692-2077 <br/>
            3909 Centre Street, San Diego, CA 92103. <br/>

          </td>
        </tr>
        
</table>
    </td
  </tr>
 <tr>
    <td>
      <br>
      If you do not want to receive these reminder emails, please click on this link to <a href=${unsubscribe_url}>unsubscribe</a>.
    </td>
  </tr>
  <tr>
    <td>
      <br>Thanks
    </td>
  </tr>
  <tr>
    <td>
      The Good To Go Team
    </td>
  </tr>
</table>
</body>
</html>



<%def name="fill_optional_string(months)">\
% if months <= 12:
since your test date at UCSD was ${visit_date}
\
% endif
</%def>\
