#!/usr/bin/env python

# think about:
# https://en.wikipedia.org/wiki/Sieve_of_Atkin
import math

primes = [2,3]

def isprime(n,store=True):

  global primes

  if n == 3 or n == 2 or n == 1:
    return True

  m = int(math.sqrt(n))+1
  for i in primes:
    if n%i == 0:
      return False
    if i > m:
      primes.append(n)
      return True

  i = primes[-1]
  while i < m:
    if n%i == 0:
      return False
    i+= 2

  if store:
    primes.append(n)
  return True

def findfeb():

  a = 1
  b = 1
  while True:
    c = a + b
    a = b
    b = c

    if c > 227000:
      if isprime(c,store=False):
        return c


dd = dict()
c = findfeb()+1
m = int(math.sqrt(c))+1

print str(c-1)

while not c == 1:
  d = 2

  if c%d == 0:
    dd[d] = 1
    c = c/d

  d = 3
  while d < m:

    if c%d == 0:
      dd[d] = 1
      c = c/d

    while True:
      d += 2

      if isprime(d):
        break

print dd.keys()
print sum(list(dd.keys()))
