#!/usr/bin/env python

import random

def mov(x):
  if x == 11:
    return 10
  elif x == 0:
    return 1
  else:
    return x+random.choice([-1,1,1,1])

def dir(p1,p2):
  if p1[0] > p2[0]:
    print "w",
  elif p1[0] < p2[0]:
    print "e",
  elif p1[1] > p2[1]:
    print "n",
  elif p1[1] < p2[1]:
    print "s",
  else:
    print "FUCK!!",

a="\
* 8 1 7 8 8 5 2 9 5 9 5\n\
8 5 1 1 5 6 9 4 4 5 2 1\n\
7 2 3 5 2 9 2 6 9 3 9 4\n\
9 2 5 9 8 9 5 7 7 5 9 6\n\
2 4 6 7 1 4 2 6 6 2 5 8\n\
2 8 1 5 3 8 4 9 7 5 2 3\n\
2 9 3 5 6 7 2 4 9 4 2 5\n\
6 3 1 7 8 2 3 3 6 7 9 3\n\
2 5 7 4 2 7 8 5 5 3 5 8\n\
5 2 9 8 3 6 1 4 9 5 6 3\n\
4 6 9 8 5 4 9 7 6 4 6 8\n\
2 7 7 1 9 9 7 3 7 2 2 ^".split("\n")

l=list()
for b in a:
  l.append(b.split(" "))

p = list()
c = 444
x = 0
y = 0
i = 0
l[0][0]='0'
l[11][11]='0'

while True:
  if random.choice([True,False]):
    x = mov(x)
  else:
    y = mov(y)

  p.append((x,y))

  if c==5 and x==11 and y==11:
    break

  c -= (int(l[y][x])+i)
  i += 1

  if c < 5  or (x==11 and y==11):
    p = list()
    c = 444
    x = 0
    y = 0
    i = 0

op = (0,0)
for i in xrange(0,len(p)):
  dir(op,p[i])
  op = p[i]
