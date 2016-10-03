#!/usr/bin/env python

import urllib
import json
import sys

if len(sys.argv) > 1:
  symbol = str(sys.argv[1])
  a = urllib.urlopen("http://www.google.com/finance/info?q=%s" % (symbol))
  b = json.loads(a.read().replace("\n","")[2:])
  out = "%s:" % (symbol)
  for a in b:
    out += "%s " % (a['l'])
  print out
