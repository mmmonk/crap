#!/usr/bin/python

from __future__ import print_function

import time
from struct import pack,unpack
from hmac import HMAC
from hashlib import sha1
from base64 import b32decode
import os
import sys


def hotp(key,counter):
  """
  http://tools.ietf.org/html/rfc4226
  """
  # convert counter to raw bytes
  b = pack(">q", counter)

  # generate HMAC-SHA1 from timestamp based on secret key
  hm = HMAC(key, b, sha1).digest()

  # extract 4 bytes from digest based on LSB
  offset = ord(hm[-1]) & 0x0F
  truncatedHash = hm[offset:offset+4]

  # get the code from it
  code = ((unpack(">L", truncatedHash)[0]) & 0x7FFFFFFF ) % 1000000

  return "0"*(6-len(str(code)))+str(code)

def totp(key):
  """
  http://tools.ietf.org/html/rfc6238
  """
  return hotp(key,int(time.time())//30)

if __name__ == "__main__":

  try:
    fd = open(os.getenv("HOME")+"/.gauth.conf")
  except:
    print("Can't read ~/.gauth.conf file")
    sys.exit(1)

  td = 30 - (int(time.time()) % 30)  # reminder of the current time

  print("time: ["+(td*"#").ljust(30,".")+"]")

  lines = fd.read().split("\n")
  for s in lines:
    try:
      s = s.split("|")
      secretkey = b32decode(s[1].replace(" ","").rstrip().upper())
    except:
      continue

    print(str(s[0]).ljust(30,".")+": "+totp(secretkey))
    s = fd.read()
  fd.close()
