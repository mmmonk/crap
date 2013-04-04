#!/usr/bin/env python

import sys

m = "attack at dawn"

try:
  c = sys.argv[1].decode('hex')
except:
  c = "09e1c5f70a65ac519458e7e53f36".decode('hex')
m2 = "attack at dusk"

key = "".join([ chr(ord(m[i])^ord(c[i])) for i in range(len(m))])
print "".join([ chr(ord(key[i])^ord(m2[i])) for i in range(len(m2))]).encode('hex')

