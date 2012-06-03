#!/usr/bin/python

import sys
import operator

try:
  data = open("memory_report_main.dat",'r')
except IOError as errs:
  print "ERROR: please specify a correct filename ("+str(errs)+")"
  sys.exit(1)

devsxd = {}
devsmd = {}
devsad = {}
devlmx = {}
devlmi = {}
devlav = {}
devtsm = {}

try:
  for line in data.readlines():
    dat = line.strip().split(',')
    ts = int("".join(dat[1].split("-")))
    try:
      if devtsm[dat[0]] < ts:
        devsmd[dat[0]] += int(dat[2]) - devlmi[dat[0]]
        devsxd[dat[0]] += int(dat[3]) - devlmx[dat[0]]
        devsad[dat[0]] += int(dat[4]) - devlav[dat[0]]
        devtsm[dat[0]] = ts
      else:
        continue
    except:
      devtsm[dat[0]] = ts
      devsmd[dat[0]] = 0
      devsxd[dat[0]] = 0
      devsad[dat[0]] = 0

    devlmi[dat[0]] = int(dat[2])
    devlmx[dat[0]] = int(dat[3])
    devlav[dat[0]] = int(dat[4])

except:
  print "ERROR: probably corrupted file, please check that there are no additional commas"
  sys.exit(1)


for st in sorted(devsad.iteritems(), key=operator.itemgetter(1),reverse=True):
  dev = st[0]
  if devsmd[dev] <= 0 and devsxd[dev] <= 0 and devsad[dev] <= 0:
    continue 
  print str(dev)+" "+str(devsmd[dev])+" "+str(devsxd[dev])+" "+str(devsad[dev])
