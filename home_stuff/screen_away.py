#!/usr/bin/env python

import os
import sys
import time

ggcmdfile = os.environ['HOME']+"/.gg/cmd"

def ekgcmd(cmd):
  fcmd = open(ggcmdfile,'w')
  fcmd.write(cmd+"\n")
  fcmd.close()

try:
  name = os.environ['STY']
except KeyError: 
  print "not running inside screen, exiting"
  sys.exit(1)

state=1

while 1:
  pipe = os.popen('screen -ls','r')
#  pipe = Popen(["screen", "-ls"], stdout=PIPE).communicate()[0]
  line = 1
  while(line):
	line = pipe.readline()
	line = line.lower()
	if state == 2 and 'attached' in line and name in line:
	  ekgcmd("connect")
	  state = 1
	if state == 1 and 'detached' in line and name in line:
	  ekgcmd("disconnect")
	  state = 2
  pipe.close()
  time.sleep(5)
