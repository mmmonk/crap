#!/usr/bin/env python

# $Id$

import sys
import string
import re


def get_os(fd):
  while 1:
    seek = fd.tell()
    line = fd.readline()
    if line:
      line = line.strip()
      
      if re.match(pattern,line):
        fd.seek(seek)
        return 0
      else:
        print line

    else:
      return 0

try:
	fs = open(sys.argv[1],'r')
except:
	print "usage: "+sys.argv[0]+" get_tech_file"
	sys.exit(2)


pattern = re.compile('^get .+')
inside = "no"
end = 1 
while end:
  line = fs.readline()
  if line:
    line = line.strip()

    if re.match(pattern,line):
      print line
      inside = line
    
    else:
      if inside == "get envar":
          print line
           
      if inside == "get os":
        get_os(fs)
  else:
    end = 0
