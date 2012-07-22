#!/usr/bin/python

# $Id: 20120722$
# $Date: 2012-07-22 13:49:17$
# $Author: Marek Lukaszuk$

import sys

file = sys.argv[1]

m = open(file).read()
p = open("/dev/urandom").read(len(m))

i = 0
ct = ""
while i < len(m):
  ct += chr(ord(m[i])^ord(p[i]))
  i += 1

print "m : "+m.encode('hex')
print "p : "+p.encode('hex')
print "ct: "+ct.encode('hex')

