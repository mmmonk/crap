#!/usr/bin/env python

import sys

def isprime(n):

  if n == 3 or n == 2 or n == 1:
    return True

  if n%2 == 0:
    return False

  i = 3
  m = (n+1)/2
  while i < m:
    if n%i == 0:
      return False
    i+= 2

  return True

a = 1
b = 1
c = 0
while True:

  c = a + b

  print str(a)+"+"+str(b)+"="+str(c)

  a = b
  b = c

  if c > 227000:
    if isprime(c):
      print c
      break

dd = dict()

c += 1
co = c

print co

while True:
  d = 2

  while True:

    if c%d == 0:
      dd[d] = 1
      c = c/d

    while True:
      d += 1

      if isprime(d):
        break

    if d > (co-1)/2:
      break

  if c == 0 or isprime(c):
    print c
    break

print dd.keys()

s = 0
for x in dd.keys():
  s += x

print s
