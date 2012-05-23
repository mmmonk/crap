#!/usr/bin/python

import sys

filename = sys.argv[1]

try:
  data = open(filename,'r')
except IOError as errs:
  print "ERROR: please specify a correct filename ("+str(errs)+")"
  sys.exit(1)

max_v = 0
min_v = 100
stime = ""
s_val = 0
etime = ""
e_val = 0
vals  = []

try:
  for line in data.readlines():
    dat = line.strip().split(',')
    ts = dat[0]
    val = int(dat[2])

    if stime == "":
      stime = ts
      s_val = val
    etime = ts
    e_val = val
    vals.append(val)

    if val > max_v:
      max_v = val
    
    if val < min_v:
      min_v = val

except:
  print "ERROR: probably corrupted file, please check that there are no additional commas"
  sys.exit(1)

avrg = 0
for val in vals:
  avrg += val
avrg /= len(vals)

print "Device name "+str(filename.replace(".csv",""))+"\
 polled from date "+str(stime)+" to "+str(etime)+"\
 had a memory increase of "+str(e_val-s_val)+"%\
 with a minimum of "+str(min_v)+"%, max of "+str(max_v)+"%\
 and average of "+(str(avrg))+"%"
 
