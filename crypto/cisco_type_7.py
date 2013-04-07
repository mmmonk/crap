#!/usr/bin/env python

# $Id: 20130407$
# $Date: 2013-04-07 13:50:27$
# $Author: Marek Lukaszuk$

# based on:
# http://wiki.nil.com/Deobfuscating_Cisco_IOS_Passwords

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

      return out
    except:
      return ""


  def encode(self,pwd,i=-1):
    import random

    if i < 0 or i > len(self.v)+1:
      i = random.randint(0,len(self.v)+1)

    out = chr(i)
    for c in pwd:
      out += chr(ord(c) ^ ord(self.v[i]))
      i = (i+1)%53

    return out.encode('hex')


def decode(s):
  ct7 = cisco_pwd_t7()
  return ct7.decode(s)

def encode(s):
  ct7 = cisco_pwd_t7()
  return ct7.encode(s)

if __name__ == "__main__":
  import sys

  ct7 = cisco_pwd_t7()

  for line in sys.stdin.read().split("\n"):
    print str(line)+" : "+ct7.decode(line)
