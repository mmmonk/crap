#!/usr/bin/python

from __future__ import print_function

import time
from struct import pack,unpack
from hmac import HMAC
from hashlib import sha1
from base64 import b32decode
from urllib import quote
import subprocess 
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

def totp(key,timeblock):
  """
  http://tools.ietf.org/html/rfc6238
  """
  return hotp(key,int(time.time())//timeblock)

def decodesecret(textsecret):
  """
  decode the b32 encoded secret
  """
  return b32decode(textsecret.replace(" ","").rstrip().upper())

def qrcodegen(account, textsecret, issuer=None):
  """
  qrcodes generator for Google Authenticator app
  using: qrencode and display from ImageMagick
  """
  cmd = "qrencode -s 10 -o - otpauth://totp/"+quote(account)+\
      "?secret="+textsecret.replace(" ","").upper()
  if issuer:
    cmd += "&issuer="+quote(issuer)

  cmd = cmd.split(" ")
  p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
  (qrpng, temp) = p.communicate() 
  p = subprocess.Popen(["display"], stdin=subprocess.PIPE)
  p.communicate(qrpng)

if __name__ == "__main__":

  LINEWIDTH = 30
  TIMEBLOCK = 30

  try:
    fd = open(os.getenv("HOME")+"/.gauth.conf")
  except:
    print("Can't read ~/.gauth.conf file\n"+\
        "format of that file should be:\n"+\
        "username|secret\n")
    sys.exit(1)

  # reminder of the current tim
  td = TIMEBLOCK - (int(time.time()) % TIMEBLOCK)

  sys.stderr.write("time: ["+(td*"#").ljust(LINEWIDTH,".")+"]\n")

  lines = fd.read().split("\n")
  for s in lines:
    try:
      s = s.split("|")
      secretkey = decodesecret(s[1]) 
    except:
      continue

    if len(sys.argv) > 1:
      if sys.argv[1] in s[0]:
        print(str(s[0][:LINEWIDTH]).ljust(LINEWIDTH,".")+": "+\
            totp(secretkey,TIMEBLOCK))
        if len(sys.argv) > 2 and sys.argv[2] == "qr":
          try:
            qrcodegen(s[0],s[1])
          except KeyboardInterrupt: 
            pass
    else:
      print(str(s[0][:LINEWIDTH]).ljust(LINEWIDTH,".")+": "+\
          totp(secretkey,TIMEBLOCK))
    s = fd.read()
  fd.close()
