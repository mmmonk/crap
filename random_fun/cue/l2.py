#!/usr/bin/env python

primes = [2,3]

def isprime(n):

  global primes

  if n == 3 or n == 2 or n == 1:
    return True

  m = (n+1)/2
  for i in primes:
    if n%i == 0:
      return False
    if i > m:
      break

  i = primes[-1]
  while i < m:
    if n%i == 0:
      return False
    i+= 2

  primes.append(n)
  return True

def findfeb():

  a = 1
  b = 1
  c = a
  while True:

    c = a + b
    a = b
    b = c

    if c > 227000:
      if isprime(c):
        return c


dd = dict()
c = findfeb()+1
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
    break

print dd.keys()

s = 0
for x in dd.keys():
  s += x

print s
