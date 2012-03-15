#!/usr/bin/python

import sys

fname = sys.argv[1]
nump  = int(sys.argv[2])
numn  = int(sys.argv[3])


m = open(fname).read()
print "m0 : "+m.encode('hex')
for enc in xrange(1,nump): 
  p = open("/dev/urandom").read(len(m))

  i = 0
  ct = ""
  while i < len(m):
    ct += chr(ord(m[i])^ord(p[i]))
    i += 1

  print "p"+str(enc)+" : "+p.encode('hex')
  print "ct"+str(enc)+": "+ct.encode('hex')

