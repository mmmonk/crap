#!/usr/bin/env python

import urllib2

url = "http://challenge.cueup.com/static/numbers.csv"

a = [int(x) for x in urllib2.urlopen(url).read().split(",")]
b = dict()
d = list()

def fs(a1,s):
  global b
  global d

  if s in a1:
    return 0

  if s > max(a1):
    return -1

  if len(a1) == 0:
    return -1

  for e in a1:
    a2 = a1[:]
    a2.remove(e)
    r = fs(a2,s+e)
    if r == 0:
      d.append(e)
      if not b.has_key(str(d)):
        b[str(d)] = 1
      d = list()
    elif r >= 0:
      b.append(r)

while True:

  c = a[:]
  d = list()
  while True:
    e = random.choice(c)
    c.remove(e)

    if len(c) == 0:
      break

    d.append(e)

    if sum(d) < min(c):
      continue

    if sum(d) > max(c):
      break

    ok = False
    for z in c:
      if sum(d) == z:
        ok = True

    if ok:
      d.sort()
      if not b.has_key(str(d)):
        b[str(d)]= 1
        print str(len(b))+" - "+str(d)+" = "+str(sum(d))
        break

