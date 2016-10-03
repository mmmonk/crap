#!/usr/bin/env python

import urllib
import json
import sys
import os
import time

if len(sys.argv) > 1:
  symbol = str(sys.argv[1])
  path = "%s/%s/.cache/stock_%s.txt" % (os.getenv('HOME'), os.getlogin(), symbol)
  out = ""
  if os.path.exists(path) and time.time() - os.stat(path).st_mtime < 600:
    out = open(path).read()
  else:
    a = urllib.urlopen("http://www.google.com/finance/info?q=%s" % (symbol))
    b = json.loads(a.read().replace("\n","")[2:])
    out = "%s:" % (symbol)
    for a in b:
      out += "%s " % (a['l'])
    open(path,"w").write(out)
  print out
