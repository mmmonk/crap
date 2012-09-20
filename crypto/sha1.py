#!/usr/bin/env python

# $Id: 20120920$
# $Date: 2012-09-20 14:24:09$
# $Author: Marek Lukaszuk$

import sys
import struct

# https://en.wikipedia.org/wiki/SHA-1

def rol32(word,count):
  word = (word << count | word >> (32 - count)) & 0xFFFFFFFF
  return word

def mod32(val):
  return val % 4294967296

def padding(msglen):
  chunks = int((msglen+9)/64)
  missing_chunks = 64 - abs((chunks*64)-(msglen+9))

  pad = "\x80"
  for i in xrange(0,missing_chunks):
    pad += "\x00"
  pad += struct.pack('>Q',msglen*8)

  return pad

h0 = 0x67452301
h1 = 0xEFCDAB89
h2 = 0x98BADCFE
h3 = 0x10325476
h4 = 0xC3D2E1F0

if sys.argv[1] == '-x':
  msg = sys.argv[2].decode('hex')
else:
  msg = sys.argv[1]
msglen = len(msg)

print "msg: "+str(msg)

msg += padding(msglen)

nchunk = 0
for i in xrange(0,int(len(msg)/64)):
  chunk = msg[nchunk*64:(nchunk+1)*64]
  nchunk += 1
  w = list(struct.unpack('>IIIIIIIIIIIIIIII',chunk))
  for j in xrange(16,80):
    w.append(rol32(w[j-3] ^ w[j-8] ^ w[j-14] ^ w[j-16],1))

  a = h0
  b = h1
  c = h2
  d = h3
  e = h4

  for j in xrange(0,80):
    if j < 20:
      f = (b & c) | ((~ b) & d)
      k = 0x5A827999
    elif j < 40:
      f = b ^ c ^ d
      k = 0x6ED9EBA1
    elif j < 60:
      f = (b & c) | (b & d) | (c & d)
      k = 0x8F1BBCDC
    else:
      f = b ^ c ^ d
      k = 0xCA62C1D6

    temp = mod32(rol32(a,5) + f + e + k + w[j])
    e = d
    d = c
    c = rol32(b,30)
    b = a
    a = temp

  h0 = mod32(h0 + a)
  h1 = mod32(h1 + b)
  h2 = mod32(h2 + c)
  h3 = mod32(h3 + d)
  h4 = mod32(h4 + e)

hash = hex(h0).rjust(10,"0")+hex(h1).rjust(10,"0")+hex(h2).rjust(10,"0")+hex(h3).rjust(10,"0")+hex(h4).rjust(10,"0")

print hash.replace("0x","").replace("L","")
