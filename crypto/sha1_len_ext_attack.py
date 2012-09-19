#!/usr/bin/env python

import sys
import struct

# https://en.wikipedia.org/wiki/SHA-1

def rol32(word,count):
  word = (word << count | word >> (32 - count)) & 0xFFFFFFFF
  return word

mod32 = 0xffffffff
h0 = 0x67452301
h1 = 0xEFCDAB89
h2 = 0x98BADCFE
h3 = 0x10325476
h4 = 0xC3D2E1F0

msg = sys.argv[1]
msglen = len(msg)

chunks = int((msglen+9)/64)
missing_chunks = 64 - abs((chunks*64)-(msglen+9))

msg += "\x80"
for i in xrange(0,missing_chunks):
  msg += "\x00"
msg += struct.pack('Q',msglen)

nchunk = 0
for i in xrange(0,int(len(msg)/64)):
  chunk = msg[nchunk*64:(nchunk+1)*64]
  print str(i)+": "+str(chunk).encode('hex')+"|"
  nchunk += 1
  w = struct.unpack('>IIIIIIIIIIIIIIII',chunk)
  w = list(w)
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

    temp = (rol32(a,5) + f + e + k + w[j]) % mod32
    e = d
    d = c
    c = rol32(b,30)
    b = a
    a = temp

  h0 = (h0 + a) % mod32
  h1 = (h1 + b) % mod32
  h2 = (h2 + c) % mod32
  h3 = (h3 + d) % mod32
  h4 = (h4 + e) % mod32

hash = hex(h0)+hex(h1)+hex(h2)+hex(h3)+hex(h4)

print hash.replace("0x","").replace("L","")
