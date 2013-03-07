#!/usr/bin/env python

import random

a = [int(x) for x in open("numbers.csv").read().split(",")]
b = dict()

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

