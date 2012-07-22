#!/usr/bin/python

# $Id: 20120722$
# $Date: 2012-07-22 13:49:30$
# $Author: Marek Lukaszuk$

import sys
from os import write

f1 = sys.argv[1]
f2 = sys.argv[2]

def sxor(a,b):
  if a > b:
    c = [ chr(ord(a[i])^ord(b[i])) for i in xrange(0,len(b))]
  else:
    c = [ chr(ord(a[i])^ord(b[i])) for i in xrange(0,len(a))]

  return "".join(c)

write(1,sxor(open(f1).read(),open(f2).read()))
