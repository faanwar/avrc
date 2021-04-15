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
    It's been a while. We miss you as much as we miss a night out in Hillcrest - and, well, we really miss a night out in Hillcrest.  
    </td>
  </tr>
  <tr>
    <td align="left">
    <br>
    While the pandemic forced Good to Go to adjust its services and availability this past year, we are thrilled to share that we are ramping up appointments again. We'd love to see you.  
    </td>
  </tr>
   <tr>
    <td align="left">
    <br>
    Over the next few weeks, we'll be reinstating our appointment reminders so keep an eye out for that in your inbox. Or, if you know you're due for a sexual health check-up, you can call to schedule an appointment now: (619) 543-9340. (<b>Please note:</b> COVID-19 guidelines will be followed closely during your appointment; you can <a href="https://www.goodtogosd.com/">visit our website</a> to learn how we do it.) 
    </td>
  </tr>
  <tr>
    <td align="left">
    <br>
    Until then, we encourage you to connect with Good to Go online:
    </td>
  </tr>
  <tr>
    <td>
    <br>
 
       <table width="100%" border="0" cellspacing="100%" cellpadding="0" padding="10px">

       <tr>
          <td>
          <br>
            <a href="https://goodtogosd.us7.list-manage.com/subscribe?u=3866fc616ec327959df0c6dce&id=e81b0e013d">Sign up for our brand-new (and totally awesome!) monthly eNewsletter.</a> The Low-Down to gain access to sexual wellness tips and one-on-one interviews with the sex-positive San Diegans we all love; and,
          </td>
        </tr>

        <tr>
          <td>
          <br>
            <a href="https://www.facebook.com/Good2GoSD">Follow us on Facebook</a> <a href="https://www.instagram.com/good2gosd/">and/or Instagram.</a> to stay up-to-speed on our sexual wellness virtual events and giveaways.
          </td>
        </tr>
   
        
</table>
    </td
  </tr>
 
  <tr>
    <td>
      <br>See you soon! 
    </td>
  </tr>
  <tr>
    <td>
      - Your Friends at Good to Go 
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
