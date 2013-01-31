#!/usr/bin/env python

# $Id: 20130131$
# $Date: 2013-01-31 17:12:43$
# $Author: Marek Lukaszuk$

import time
import sys
import re
import argparse

fmt = [
    ["[A-Z][a-z]{2}\s+\d+\s+\d+:\d+:\d+","%b %d %H:%M:%S",1,6], #Jan 12 12:32:54
    ["[A-Z][a-z]{2}\s+\d+\s+\d+:\d+","%b %d %H:%M",1,5], #Jan 12 12:32
    ["\d+\s+\d+:\d+:\d+","%d %H:%M:%S",2,6], # 12 12:32:54
    ["\d+\s+\d+:\d+","%d %H:%M",2,5], # 12 12:32
    ["\d+:\d+:\d+","%H:%M:%S",3,6], # 12:32:54
    ["\d+:\d+","%H:%M",3,5], # 12:32
]
def rematch(line,t,ff):
  m = re.match(ff[0],line) 
  if m:
    return time.strptime(m.group(0),ff[1])
  return t 

def converttime(line,dt=0):
  
  t = (time.localtime(int(dt)),0,1)
  i = 0
  while (i<len(fmt)):
    t = rematch(line,t,fmt[i])
    i += 1

  return (t[0],

if __name__ == "__main__":
  
  p = argparse.ArgumentParser(description='tgrep - time grep')
  p.add_argument("stime",help="Time or date from which to start printing log lines, or - for none")
  p.add_argument("etime",default="-",help="Time or date at which to end printing log lines, or - for none")

  args = p.parse_args()
  
  try:
    ts = converttime(args.stime)
  except:
    p.print_help()
    sys.exit(1)

  try:
    te = converttime(args.etime,9999999999)
  except:
    p.print_help()
    sys.exit(1)

  try:
    for line in sys.stdin.readlines():

      lt = converttime(line)[0]
      if lt[ts[1]:ts[2]] > ts[ts[1]:ts[2]] and lt[te[1]:te[2]] < te[te[1]:te[2]]: 
        print line,
  except:
    pass
