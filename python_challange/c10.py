#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/return/bull.html
# data: http://www.pythonchallenge.com/pc/return/sequence.txt

# len(a[30]) = ?
# a = [1, 11, 21, 1211, 111221, ...
# https://en.wikipedia.org/wiki/Look-and-say_sequence

b = "1"
i = 1

while True:
  c = 0
  l = 0
  a = ""
  for d in b:
    if l == d:
      c += 1
    else:
      if c > 0:
        a += str(c)+str(l)
      c = 1
    l = d

  a += str(c)+str(l)

  b = a
  print str(i)+": "+str(a)

  if i == 30:
    print len(a)
    break

  i += 1

