#!/usr/bin/env python

# $Id: 20130212$
# $Date: 2013-02-12 13:35:31$
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
def rematch(line,ff):
  m = re.match(ff[0],line) 
  if m:
    return True
  return False

def converttime(line,ifmt=-1):
 
  if ifmt == -1:
    i = 0
    while (i<len(fmt)):
      if rematch(line,fmt[i]) == True:
        ifmt = i
        break
      i += 1
 
  if ifmt == -1:
    return (ifmt,0)

  m = re.match(fmt[ifmt][0],line)
  return (ifmt,time.strptime(m.group(0),fmt[ifmt][1]))

if __name__ == "__main__":
  
  p = argparse.ArgumentParser(description='tgrep - time grep')
  p.add_argument("stime",help="Time or date from which to start printing log lines, or - for none")
  p.add_argument("etime",default="-",help="Time or date at which to end printing log lines, or - for none")

  args = p.parse_args()
  
  ts = converttime(args.stime)
  te = converttime(args.etime)

  print "|"+str(ts)+"| |"+str(te)+"|"
  sys.exit(0)
  try:
    for line in sys.stdin.readlines():

      lt = converttime(line)
      if lt[ts[1]:ts[2]] > ts[ts[1]:ts[2]] and lt[te[1]:te[2]] < te[te[1]:te[2]]: 
        print line,
  except:
    pass
