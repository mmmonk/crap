#!/usr/bin/env python

import sys
import os

def valconv(value):
  try:
    return int(value)
  except ValueError:
    return int(value,16)

s_offset = 0x00
e_offset = 0x00
o_pattern = "ff"
filename = ""

# options parsing
i = 1
imax = len(sys.argv)
try:
  while 1:
    if i >= imax:
      break
    arg = sys.argv[i]
    if arg == "-so":
      i += 1
      s_offset = valconv(sys.argv[i])
    elif arg == "-eo":
      i += 1
      e_offset = valconv(sys.argv[i])
    elif arg == "-p":
      i += 1
      o_pattern = sys.argv[i]
    else:
      filename = sys.argv[i]
    i += 1
except:
  sys.exit(1)

if filename == "":
  sys.exit(1)

try:
  c = o_pattern.decode('hex')
except TypeError:
  sys.exit(1)

if e_offset == 0:
  e_offset = s_offset + 0x32

max_offset = os.stat(filename)[6]

if e_offset < 0 or e_offset > max_offset:
  e_offset = max_offset

for offset in xrange(s_offset,e_offset):
  nfile = str(hex(offset))+"_"+str(o_pattern)+"_"+filename
  os.system("cp "+str(filename)+" "+str(nfile))

  fd = open(nfile,"r+b")
  fd.seek(offset)
  fd.write(c)
  fd.close()

