#!/usr/bin/env python


import smtplib 
import poplib

who = 'build@pica8.local'
whos = "lpi@pica8.local"
subject = 'SMTP e-mail test'

message = """
From: %(who)s
To: %(whos)s
Subject: %(subject)s
This is a test e-mail message.
"""%{'who': who, 'whos':whos, 'subject': subject}

try:
    smtpObj = smtplib.SMTP('10.10.50.11')
    smtpObj.sendmail(who, [whos], message) 
    print "Successfully sent email"

except:
    print "Error: unable to send email"


