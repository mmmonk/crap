#!/usr/bin/env python

import urllib2

url = "http://challenge.cueup.com/static/numbers.csv"

a = [int(x) for x in urllib2.urlopen(url).read().split(",")]
b = dict()

def findsum(a1,a2):
  global b

  if len(a1) > 1:
    if sum(a1) in a2:
      a1.sort()
      if not b.has_key(str(a1)):
        b[str(a1)] = 1

    if sum(a1) > max(a2):
      return

  for e in a2:
    a11 = a1[:]
    a22 = a2[:]
    a22.remove(e)
    a11.append(e)
    findsum(a11,a22)

a.sort()
print a
findsum([],a)
print len(b)
