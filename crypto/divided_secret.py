#!/usr/bin/python

import sys
from time import sleep 

fname = sys.argv[1] # file to share
nump  = int(sys.argv[2]) # total number of people
numn  = int(sys.argv[3]) # number of people needed to decrypt

if nump < numn:
  sys.exit(1)

m = open(fname).read()
print "m0  : "+m.encode('hex')

for i in xrange(1,nump): 
  
  ct = m 
  
  for j in xrange(1,numn):
    #sleep(1)
    p = open("/dev/urandom").read(len(m))

    x = 0
    temp = ""
    while x < len(ct):
      temp += chr(ord(ct[x])^ord(p[x]))
      x += 1

    ct = temp
    print "p"+str(i)+str(j)+" : "+p.encode('hex')
  
  print "ct"+str(i)+" : "+ct.encode('hex')

