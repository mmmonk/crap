#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/def/linkedlist.html

import urllib
import sys

u = "http://www.pythonchallenge.com/pc/def/linkedlist.php?nothing="
n = "12345"
l = ""

i = 1

a = urllib.URLopener()
while True:
  b = a.open(u+n)
  t = b.read()
  l = n
  n = t.split()[-1]
  print str(i)+": "+str(t)
  i += 1
  try:
    int(n)
  except:
    if "Yes. Divide" in t:
      n = str(int(l)/2)
    else:
      sys.exit(0)

