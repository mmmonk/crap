#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/def/ocr.html

import urllib
import sys
import re

t = urllib.URLopener().open("http://www.pythonchallenge.com/pc/def/ocr.html").read().replace("\n","")
a = re.search("<!--(.%.+)-->",t,re.S).group(1)

b = dict()
for c in a:
  if b.has_key(c):
    b[c] += 1
  else:
    b[c] = 1

for d in b:
  if b[d] > 1000:
    a = a.replace(d,"")

print a
