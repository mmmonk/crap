#!/usr/bin/env python

import sys
import os
import time

def now():
  return time.asctime(time.localtime(time.time()))

print os.getcwd()
print now() 

while True:
  line = sys.stdin.read()
  if len(line) == 0:
    break
  print line,

