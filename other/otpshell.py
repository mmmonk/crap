#!/usr/bin/python

# $Id: 20120802$
# $Date: 2012-08-02 13:51:37$
# $Author: Marek Lukaszuk$

# idea from http://pastebin.com/dSJbGSBD

shell = "/usr/bin/tcsh"

from time import time,sleep
from struct import pack,unpack
from hmac import HMAC
from hashlib import sha1
from base64 import b32decode,b32encode
from random import randint
import os
import sys


func SameTimeStrCmp(v1,v2):
  res = 0

  for

  return res


# generator
otp = "{} {}{}{} {}{}{} {}{}{} {}{}{} {}{}{}".format(*b32encode(sha1(str(randint(0,9999999999999999))).digest()).lower()[:16])
shell = sys.argv[1]

try:
  fd = open(getenv("HOME")+"/.otpauth.conf")
except:
  print "Can't read ~/.otpauth.conf file"
  exit(1)

tm = int(time() / 30)

s = fd.read()
while (s != ""):
  s = s.split("|")
  secretkey = b32decode(s[1].replace(" ","").rstrip().upper())

  # convert timestamp to raw bytes
  b = pack(">q", tm)

  # generate HMAC-SHA1 from timestamp based on secret key
  hm = HMAC(secretkey, b, sha1).digest()

  # extract 4 bytes from digest based on LSB
  offset = ord(hm[-1]) & 0x0F
  truncatedHash = hm[offset:offset+4]

  # get the code from it
  code = unpack(">L", truncatedHash)[0]
  code &= 0x7FFFFFFF;
  code %= 1000000;

  print str(s[0])+": "+"0"*(6-len(str(code)))+str(code)
  s = fd.read()

os.execv(shell,sys.argv)
