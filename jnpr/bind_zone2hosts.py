#!/usr/bin/python

import sys
from re import match

arec = {}
crec = {} 

bindzone = open(sys.argv[1],"r")

for line in bindzone:
  if not match("^\s*;",line):
    dns = line.rstrip().lower().split()
    if " A " in line:
      arec[dns[0]]=dns[2]
    if " CNAME " in line:
      crec[dns[0]]=dns[2]

bindzone.close()

for k,v in crec.iteritems():
  try:
    arec[k] = arec[v]
  except:
    pass

for name,ip in sorted(arec.iteritems()):
  print ip+" "+name

