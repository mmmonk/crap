#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/def/peak.html

import urllib
import pickle
import sys

f = urllib.URLopener().open("http://www.pythonchallenge.com/pc/def/banner.p")
a = pickle.load(f)

for b in a:
  print "".join([c[0]*int(c[1]) for c in b])
