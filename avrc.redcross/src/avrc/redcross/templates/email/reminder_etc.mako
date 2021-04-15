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
Due to the current COVID-19 crisis, no elective HIV or STD testing is being performed at any of our test sites. Routine reminders will be resent when testing has re-opened and we encourage everyone to frequently check the website for updates. We apologize for the inconvenience but want to ensure the safety of staff and participants. Thank you for understanding and stay safe!
    </td>
  </tr>
 
  <tr>
    <td>
    <br>
 
       <table width="100%" border="0" cellspacing="100%" cellpadding="0" padding="10px">

       <tr>
          <td>
          <br>
            Good To Go: <br/>
            www.goodtogosd.com <br/>
            619-543-9340 <br/>
            3830 Park Boulevard, San Diego, CA 92103 <br/>
            (Corner of University Avenue and Park Boulevard)</br>


          </td>
        </tr>

       <br />

      
     
        
</table>
    </td
  </tr>
  <tr>
   <td> 
    <br>
    Please, do not reply to this email as this mailbox is unmonitored. If you have any questions, contact us at goodtogo@ucsd.edu.
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
