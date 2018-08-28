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
      According to our records, it has been more than 3 months since you last tested (using the email ${email}) at the <b>UCSD Early Test/Lead the Way
      testing program</b>. Do you think this might be a good time to schedule a repeat test?
    </td>
  </tr>
  <tr>
    <td>
    <br>
       If you would like to schedule your next appointment at the Lead the Way location, please use our online <a href=${ltw_url}>calendar</a> (or call ${phone}). 
    </td>
  </tr>
  <tr>
    <td>
    <br>
       To schedule an appointment at the location of your choice you can use the following contact information: 
       <table width="100%" border="0" cellspacing="100%" cellpadding="0" padding="10px">
        <tr>
          <td>
          <br>
            <a href="https://www.google.com/maps/place/308+University+Ave,+San+Diego,+CA+92103/@32.7484402,-117.1646623,17z/data=!3m1!4b1!4m5!3m4!1s0x80d954d087f0bdc7:0x703a2181fa9694b6!8m2!3d32.7484402!4d-117.1624736">Urban Mo's</a><br/>
            <a href="https://maps.google.com/?q=308+University+Avenue,+San+Diego,+CA+92103&entry=gmail&source=g">308 University Av, SanDiego, CA 92103</a><br/>
            Thursday: 10:00am - 4:00pm, Walk-ins. <br/>
          </td>
        </tr>
        <tr>
          <td>
          <br>
            <a href="https://www.google.com/maps/place/3830+Park+Blvd,+San+Diego,+CA+92103/@32.7482062,-117.1488138,17z/data=!3m1!4b1!4m5!3m4!1s0x80d954e88cc1ab1b:0x4ab573f94f395be4!8m2!3d32.7482062!4d-117.1466251">Lead the Way - ${phone}</a><br/>
            <a href="https://maps.google.com/?q=3830+Park+Boulevard,+San+Diego,+CA+92103&entry=gmail&source=g">3830 Park Boulevard, SanDiego, CA 92103</a><br/>
            Monday-Friday: noon - 8:00pm<br/>
            Saturday: 10:00am - 4:00pm<br/>
            or make an appointment <a href="http://leadthewaysd.com/scheduling_calendar.html">online</a>.
          </td>
        </tr>
        <tr>
          <td>
          <br>
            <a href="https://www.google.com/maps/place/220+Dickinson+St+a,+San+Diego,+CA+92103/@32.7553799,-117.1680695,17z/data=!3m1!4b1!4m5!3m4!1s0x80d954d6294c728f:0x6e667d103ae903a2!8m2!3d32.7553799!4d-117.1658808">AntiViral Research Center(AVRC) - 619-543-8080</a><br/>
            <a href="https://maps.google.com/?q=220+Dickinson+Street,+Suite+A,+San+Diego,+CA+92103&entry=gmail&source=g">220 Dickinson Street, Suite A, SanDiego, CA 92103.</a><br/>
            Monday - Thursday: 09:00am - 3:00pm,<br/>
            Friday: 09:00am - noon<br/>
          </td>
        </tr>
        <tr>
          <td>
          <br>
            <a href="https://www.google.com/maps/place/3909+Centre+St,+San+Diego,+CA+92103/@32.748886,-117.1500095,17z/data=!3m1!4b1!4m5!3m4!1s0x80d954e876536823:0xf4f026f8f62359a3!8m2!3d32.748886!4d-117.1478208">The San Diego LGBT Community Center</a><br/>
            <a href="https://maps.google.com/?q=3909+Centre+Street,+San+Diego,+CA+92103&entry=gmail&source=g">3909 Centre Street, SanDiego, CA 92103.</a><br/>
            For an appointment call 619-692-2077<br/>
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
      Early Test/Lead the Way Team
    </td>
  </tr>
  <tr>
    <td>
      <br>
      <img src="http://theearlytest.ucsd.edu:6002/static/images/logo_AVRC.jpg" height="50" align="left"/>
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
