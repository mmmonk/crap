#!/usr/bin/env python

# $Id: 20121002$
# $Date: 2012-10-02 19:23:08$
# $Author: Marek Lukaszuk$

# based on:
# http://wiki.nil.com/Deobfuscating_Cisco_IOS_Passwords

import sys,random

class cisco_pwd_t7:

  v = "dsfd;kfoA,.iyewrkldJKDHSUBsgvca69834ncxv9873254k;fg87"

  def decode(self,pwd):

    try:
      ct7 = pwd.decode('hex')
      out = ""
      i = ord(ct7[0])
      for c in ct7[1:]:
        out += chr(ord(c) ^ ord(self.v[i]))
        i = (i+1)%53

      return pwd+": "+out
    except:
      return pwd+": "


  def encode(self,pwd,i=-1):

    if i < 0 or i > len(self.v)+1:
      i = random.randint(0,len(self.v)+1)

    out = chr(i)
    for c in pwd:
      out += chr(ord(c) ^ ord(self.v[i]))
      i = (i+1)%53

    return pwd+": "+out.encode('hex')

if __name__ == "__main__":
  ct7 = cisco_pwd_t7()

  for line in sys.stdin.read().split("\n"):
    print ct7.decode(line)
