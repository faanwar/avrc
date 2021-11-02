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
    Thanks for taking an important step in your sexual health. We look forward to seeing you at Good to Go soon. 
    </td>
  </tr>

  <tr>
    <td align="left">
    <br>
    <b> In preparation for your appointment, here are a few things you should know: </b>
    </td>
  </tr>
  
 <tr>
    <td align="left">
    <br> <br>
   We observe COVID-19 precautions per the CDC's direction for healthcare settings. A brief symptom screening will be conducted upon your arrival at Good to Go, and a mask will be required throughout your appointment. (If you forget your mask, don't sweat it! We have disposable masks on-hand - just let us know.) <b>Please note:</b> CDC regulations change regularly; <a href="https://goodtogosd.us7.list-manage.com/subscribe?u=3866fc616ec327959df0c6dce&id=e81b0e013d">stay tuned to our monthly eNewsletter</a>, <a href="https://www.facebook.com/Good2GoSD">Facebook</a> or <a href="https://www.instagram.com/good2gosd/">Instagram</a> for updates on screening and masking guidelines at our clinic.
    </td>
  </tr>
   <tr>
    <td align="left">
    <br>
    As of October 2021, Good to Go offers pooled STI testing for gonorrhea and chlamydia, as opposed to single-site testing. This means that urine tests and body site swabs conducted during your sexual health check-up will be combined and tested all at once to check for infection. You might be wondering: what's the difference between pooled versus single-site testing? Here it is: if you test positive for gonorrhea or chlamydia, your results will not indicate the location of your infection. That's it, nothing else changes. We understand this update can make sharing your STI results a little challenging. That's why, we offer Partner Services to anonymously notify your partners of any positive results. All you have to do is ask your Good to Go STI treatment coordinator to connect you with Partner Services and they'll take care of the rest. Curious why we made this change? Read about <a href="https://www.goodtogosd.com/">our testing approach</a> on our website to learn how pooled testing helps our community. 
    </td>
  </tr>
   <tr>
    <td align="left">
    <br>
    Not sure what to expect at a sexual health check-up? Read a complete play-by-play of what you can expect from the second you walk into Good to Go's doors in our free online guide. We answer commonly asked questions like "Do STI tests hurt?" (spoiler: they don't) and "How quickly will I get my STI results?" (spoiler: fast) - <a href="https://www.goodtogosd.com/what-to-expect-from-sti-testing">check it out here</a>. Still have questions? We got you! Give us a call at 619-543-9340 to speak directly with one of our testers. 
    </td>
  </tr>

 <tr>
    <td>
    <br>
    <b>Where to find us:  </b><br><br>
       <table width="100%" border="0" cellspacing="100%" cellpadding="0" padding="10px">

       <tr>
          <td>
            Good to Go San Diego
          </td>
        </tr>
        <tr>
          <td>
            3830 Park Blvd. San Diego, CA 92103 (On the corner of University and Park) 
          </td>
           </tr>
           <tr>
          <td>
            Phone Number (clinic front desk): (619) 543-9340
          </td>
           </tr>
           <tr>
          <td>
            Email: goodtogo@ucsd.edu
          </td>
        </tr>
   
        
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
      <br>See you soon!
    </td>
  </tr>
  <tr>
    <td>
      - The Good to Go Team
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
