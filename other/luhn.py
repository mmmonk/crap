#!/usr/bin/env python

# $Id: 20130124$
# $Date: 2013-01-24 11:43:55$
# $Author: Marek Lukaszuk$

# based on https://en.wikipedia.org/wiki/Luhn_algorithm

import sys

try:
  num = sys.argv[1]
except:
  print "no number specified"
  sys.exit(1)

evn = [ str(int(num[i*2+1])*2) for i in xrange(0,len(num)/2)]
cs = sum([ int(num[i*2]) for i in xrange(0,len(num)/2)])

for n in evn:
  cs += sum([int(i) for i in n])

print cs
cs = cs % 10
print cs

