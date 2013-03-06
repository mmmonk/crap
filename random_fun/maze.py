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

a=open("maze.txt").read().split("\n")
l=list()
for b in a:
  l.append(b.split(" "))

p = list()
c = 444
x = 0
y = 0
i = 0
l[0][0]=0
l[11][11]=0

while True:
  if random.choice([True,False]):
    x = mov(x)
  else:
    y = mov(y)

  p.append([x,y])

  if c==5 and x==11 and y==11:
    break

  c -= (int(l[x][y])+i)

  if c < 0 or (x==11 and y==11):
    p = list()
    c = 444
    x = 0
    y = 0
    i = 0

  i += 1
op = (0,0)

for i in xrange(0,len(p)):
  dir(op,p[i])
  op = p[i]
