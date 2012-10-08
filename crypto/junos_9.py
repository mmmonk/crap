#!/usr/bin/env python

# $Id: 20121008$
# $Date: 2012-10-08 09:48:32$
# $Author: Marek Lukaszuk$

# based on:
# http://cpansearch.perl.org/src/KBRINT/Crypt-Juniper-0.02/lib/Crypt/Juniper.pm

import sys,re,random

class junos_passwd_9:

  # only global values needed
  encoding = ((1,4,32),(1,16,32),(1,8,32),(1,64),(1,32),(1,4,16,128),(1,32,64))
  len_enc = len(encoding)
  extra = {}
  num_alpha = {}

  def __init__(self):
    # we could actually hardcode all those calculations
    fam = ('QzF3n6/9CAtpu0O','B1IREhcSyrleKvMW8LXx','7N-dVbwsY2g4oaJZGUDj','iHkq.mPf5T')
    for i in xrange(0,len(fam)):
      for c in fam[i]:
        self.extra[c] = 3-i

    f = "".join(fam)
    self.num_alpha = dict([c for c in zip(f,xrange(0,len(f)))])
    self.len_num_alpha = len(self.num_alpha)

  def decode(self,pwd):
    '''
    decode Junos $9$ passwords
    '''
    chars = pwd
    if '$9$' in pwd:
      p9 = re.search("\$9\$(.+)",pwd)
      chars = p9.group(1)

    prev = chars[0]
    chars = chars[self.extra[prev]+1:]
    out = ""
    i = 0
    while (i<len(chars)):
      d = self.encoding[len(out)%self.len_enc]

      gaps = []
      for c in chars[i:i+len(d)]:
        gaps.append((self.num_alpha[c]-self.num_alpha[prev])%self.len_num_alpha-1)
        prev = c

      num = 0
      for j in xrange(0,len(gaps)):
        num += gaps[j] * d[j]

      out += chr(num % 256)
      i += len(d)

    return str(pwd)+": "+str(out)

  def encode(self,pwd):
    return str(pwd)

if __name__ == "__main__":

  jp9 = junos_passwd_9()

  print jp9.decode("$9$LbHX-wg4Z") # lc
  print jp9.decode("$9$41JDk5T3CpBFnCuB1rl8X7-VYq.5") # netscreen
