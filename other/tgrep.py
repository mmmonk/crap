#!/usr/bin/env python

# $Id: 20130130$
# $Date: 2013-01-30 23:08:18$
# $Author: Marek Lukaszuk$

import time
import sys
import argparse
import re

logtfmt = "%b %d %H:%M:%S"
argtfmt = "%b %d %H:%M:%S"

try:
  ts = time.strptime(sys.argv[1],argtfmt)
except:
  sys.exit(1)

try:
  te = time.strptime(sys.argv[2],argtfmt)
except:
  te = time.localtime(time.time())

for line in sys.stdin.readlines():

  llt = re.search("^([A-Z][a-z]{2}\s+\d+\s+\d+:\d+:\d+)",line)
  lt = time.strptime(llt.group(0),logtfmt)
  if lt > ts and lt < te:
    print line,

