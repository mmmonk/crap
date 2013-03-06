#!/usr/bin/env python

def fib(a=1,b=1):
  return a+b

def isprime(n):

  i = 2
  while True:
    if n%i == 0:
      return True
    if i == 2:
      i+= 1
    else:
      i+= 2

     if i > (n-1)/2:
       return False
  return False

while True:

