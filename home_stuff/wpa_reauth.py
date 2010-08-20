#!/usr/bin/env python

# $Id$

import subprocess 
import time
import os
import sys

SLEEP=10

def runcmd(cmd):
  try:
	retcode = subprocess.call(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
  except:
	os._exit(0)	

  return retcode 


def maincheck():
  cmd = '/sbin/ifconfig wlan0'
  output = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]

  if '172.17.177.160' in output:

	SLEEP=10

	retcode = runcmd('/usr/sbin/arping -q -c 2 -i wlan0 172.17.177.129') 

	if not retcode == 0 :

	  runcmd('/sbin/wpa_cli reassociate')
	  runcmd('/usr/bin/logger -i -t \'wpa_reauth.py\' "wpa_supplicant reassociation forced"')

  else:
	if SLEEP < 900:
	  SLEEP+=10

  time.sleep(SLEEP)


pid = os.fork()
if pid == 0:
  os.chdir('/')
  os.open('/dev/null',os.O_RDWR)
  os.dup2(0,1)
  os.dup2(0,2)
else:
  os._exit(0)

while True:

	maincheck()


