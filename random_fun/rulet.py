#!/usr/bin/env python

def gen(x):
  return (69069*x+1)%4294967296

def loop(l,x):
  xl = list()
  for j in xrange(0,len(l)):
    xl.append(gen(x))
    if not xl[j]%36 == l[j]:
      return False
    x = xl[j]
  print xl[-1]
  return True

i = 7137832
l = [27, 16, 1, 34, 31, 24, 17, 34, 35, 16, 13]

while True:

  xo = 34+36*i
  if loop(l,xo):
    print xo
    break
  if xo > 4294967296:
    print "not found"
    break
  i+=1
