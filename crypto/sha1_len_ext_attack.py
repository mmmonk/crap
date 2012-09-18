#!/usr/bin/env python

import sys

# https://en.wikipedia.org/wiki/SHA-1

h0 = 0x67452301
h1 = 0xEFCDAB89
h2 = 0x98BADCFE
h3 = 0x10325476
h4 = 0xC3D2E1F0

msg = sys.argv[1]+"\x80"
msglen = len(msg)
chunks = int(msglen/64)
missing_chunks = 56 - abs((chunks*64)-msglen)

for i in xrange(0,missing_chunks):
  msg += "\x00"

nchunk = 0
for i in xrange(0,int(len(msg)/64)):
  chunk = msg[nchunk*64:(nchunk+1)*64]
  print str(i)+": "+str(chunk).encode('hex')+"|"
  nchunk += 1

