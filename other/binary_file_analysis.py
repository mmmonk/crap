#!/usr/bin/env python

# $Id: 20130326$
# $Date: 2013-03-26 14:22:59$
# $Author: Marek Lukaszuk$

import subprocess
import os
import sys

key = "abcdefghijklmnoprstquwvxyz0123456789"

os.environ['LD_LIBRARY_PATH']="."

byte = sys.argv[1]

try:
  byte = int(byte)
except:
  sys.exit()

if byte < 1 or byte > 4:
  sys.exit()

filename = "somebinary_to_analyse_output"
query = "-e 000000 -t 1"

correct = subprocess.check_output("./somebinary_to_analyse_output "+query,shell=True).strip()
clear = subprocess.check_output("./somebinary_to_analyse_output_null "+query,shell=True).strip()

print "[+] correct: "+str(correct)
print "[+] clear:   "+str(clear)

check_1 = (int(clear,16) >> (32-((byte-1)*8))) % 256
check_2 = (int(clear,16) >> (32-((byte)*8))) % 256

print "[+] matching against "+str(byte)+" byte, which is "+hex(check_1)

off = 0
for offset in xrange(5536,5791):
  nfile = filename+"_test_1"
  os.system("cp -f "+str(filename)+" "+str(nfile))

  fd = open(nfile,"r+b")
  fd.seek(offset)
  fd.write(chr(0))
  fd.close()

  test1 = subprocess.check_output("./somebinary_to_analyse_output_test_1 "+query,shell=True).strip()
  value = (int(test1,16) >> (32-((byte-1)*8))) % 256
  if value == check_1:
    off = offset
    print "[+] Offset "+str(off)+" "+str(off-5536)
    break

print "[+] modifying offset "+str(off)+" with values from 0x00 to 0xff"

for i in range(256):

  nfile = filename+"_test_2"
  os.system("cp -f "+str(filename)+" "+str(nfile))

  fd = open(nfile,"r+b")
  fd.seek(off)
  fd.write(chr(i))
  fd.close()

  test2 = subprocess.check_output("./somebinary_to_analyse_output_test_2 "+query,shell=True).strip()
  value = (int(test2,16) >> (32-((byte)*8))) % 256
  change = chr(abs(value-check_2))

  add = 0
  ok = False
  while True:

    try:
      add = key.index(change,add)
    except:
      if not ok:
        print str(i).zfill(3)+" => "+str(off-5536).zfill(3)+" "+str(test2)
      break

    nfile1 = nfile+"2"
    os.system("cp -f "+str(nfile)+" "+str(nfile1))

    fd = open(nfile1,"r+b")
    fd.seek(5536+add)
    fd.write(chr(0))
    fd.close()

    test3 = subprocess.check_output("./somebinary_to_analyse_output_test_22 "+query,shell=True).strip()
    value1 = (int(test3,16) >> (32-((byte-1)*8))) % 256
    value2 = (int(test3,16) >> (32-((byte)*8))) % 256
    if value2 == check_2:
      print str(i).zfill(3)+"("+str(value1).zfill(3)+") => "+str(add).zfill(3)+" "+str(test2)+" "+str(test3)
      ok = True
      break
    add += 1

