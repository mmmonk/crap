#!/usr/bin/python

import os
import smtplib

sender = 'mlukaszuk@company.gov'
receivers = ['mlukaszuk@company.gov']

MAINDIR = "/home/case/store/company/nsmdiff/.tosend"

for filename in os.listdir(MAINDIR):
  message = open(MAINDIR+"/"+filename,'r').read()
 
  smtpObj = smtplib.SMTP('mail.company.gov')
  smtpObj.sendmail(sender, receivers, message)
  os.unlink(MAINDIR+"/"+filename)  
