#!/usr/bin/python

# $Id: 20120809$
# $Date: 2012-08-09 16:38:17$
# $Author: Marek Lukaszuk$

# idea from http://pastebin.com/dSJbGSBD

shell = "/usr/bin/tcsh"

from time import time,sleep
from struct import pack,unpack
from hmac import HMAC
from hashlib import sha1
from base64 import b32decode,b32encode
from random import randint
from getpass import getpass
import os
import sys


def constantTimeCompare(a, b):
    if isinstance(a, unicode):
        if not isinstance(b, unicode):
            raise inputMismatchError
        isPy3Bytes = False
    elif isinstance(a, bytes):
        if not isinstance(b, bytes):
            raise inputMismatchError
        isPy3Bytes = sys.version_info >= (3, 0)
    else:
        raise inputMismatchError

    if isPy3Bytes:
        for x, y in zip(a, b):
            result |= x ^ y
    else:
        for x, y in zip(a, b):
            result |= ord(x) ^ ord(y)
    return result == 0

def genotp():
  return "{} {}{}{} {}{}{} {}{}{} {}{}{} {}{}{}".format(*b32encode(sha1(str(randint(0,9999999999999999))).digest()[:10]).lower())

def otpchk(key, response):

  tm = int(time() / 30)
  for delta in (-1,0,1):
    s = key.replace(" ","").rstrip().upper()
    secretkey = b32decode(s)

    # convert timestamp to raw bytes
    b = pack(">q", tm+delta)

    # generate HMAC-SHA1 from timestamp based on secret key
    hm = HMAC(secretkey, b, sha1).digest()

    # extract 4 bytes from digest based on LSB
    offset = ord(hm[-1]) & 0x0F
    truncatedHash = hm[offset:offset+4]

    # get the code from it
    code = unpack(">L", truncatedHash)[0]
    code &= 0x7FFFFFFF;
    code %= 1000000;

    code = "0"*(6-len(str(code)))+str(code)

    if constantTimeCompare(code,response):
      return True

  return False

try:
  shell = sys.argv[1]
except:
  pass

try:
  open(os.getenv("HOME")+"/.otpauth.conf")
except:
  print "Can't read ~/.otpauth.conf file"
  exit(1)

pw = getpass("pass: ")
if otpchk(open(os.getenv("HOME")+"/.otpauth.conf").read(),pw.strip()):
  print "Cool"

#os.execv(shell,sys.argv)
