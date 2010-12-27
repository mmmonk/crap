#!/usr/bin/python

import os
import smtplib
import sys
import re

conffile='/home/case/.nsmauth.conf'

def LoadConf(filename):

  global confvar

  confvar = {}
  try:
    conf=open(filename,'r')
  except:
    print "error during conf read"
    sys.exit(1)

  line = conf.readline()

  while line:
    conft = line.replace('\n','').split("=")
    confvar[conft[0]]=conft[1]
    line = conf.readline()

LoadConf(conffile)

email_pattern = re.compile("[-a-zA-Z0-9._]+@[-a-zA-Z0-9_]+.[a-zA-Z0-9_.]+")

sender = re.findall(email_pattern,confvar['emailfrom'])[0] 
receivers = re.findall(email_pattern,confvar['emailto'])

MAINDIR = confvar['nsmdiffdir']+"/.tosend"

if os.path.exists(MAINDIR):
  for filename in os.listdir(MAINDIR):
    message = open(MAINDIR+"/"+filename,'r').read()
   
    smtpObj = smtplib.SMTP(confvar['emailsmtp'])
    smtpObj.sendmail(sender, receivers, message)
    os.unlink(MAINDIR+"/"+filename)  
