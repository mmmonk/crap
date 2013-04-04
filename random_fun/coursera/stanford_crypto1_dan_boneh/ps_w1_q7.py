#!/usr/bin/env python

import sys

m = "attack at dawn"

try:
  c = sys.argv[1].decode('hex')
except:
  c = "09e1c5f70a65ac519458e7e53f36".decode('hex')
n = "attack at dusk"

print "  m = "+str(m)
print "  c = "+str(c).encode('hex')
key = "".join([ chr(ord(m[i])^ord(c[i])) for i in range(len(m))])
print "m^c = k = "+str(key).encode('hex')
print "  n = "+str(n)
print "n^k = "+"".join([ chr(ord(key[i])^ord(n[i])) for i in range(len(n))]).encode('hex')

