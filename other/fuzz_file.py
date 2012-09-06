#!/usr/bin/env python

import sys
import os

filename = sys.argv[1]
s_offset = 0
e_offset = -1
o_char = "a"
iterations = 0

max_offset = os.stat(filename)[6]

if e_offset == -1 or e_offset > max_offset:
  e_offset = max_offset

if not o_char == "":
  c = ord(o_char)

for offset in xrange(s_offset,e_offset):
  if o_char == "":
    for c in xrange(0,256):
      nfile = str(offset)+"_"+str(hex(c))+"_"+filename
      print str(nfile)+" "+str(filename)
  else:
    nfile = str(offset)+"_"+str(hex(c))+"_"+filename
    print str(nfile)+" "+str(filename)
#  fd = open(filename,"r+b")
#  fd.seek(offset)
#  fd.write("\xff")
#  fd.close()

