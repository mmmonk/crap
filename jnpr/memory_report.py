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
day = ""
cday = ""

try:
  fd = open("memory_report_main.dat","ab")
except:
  print "problem with writting to the file memory_report_main.dat"
  sys.exit(1)

try:
  for line in data.readlines():
    dat = line.strip().split(',')
    ts = dat[0]
    val = int(dat[2])
    
    day = dat[0].split(" ")[0]
    
    if day != cday:
      if cday != "":
        avrg = 0
        for val in vals:
          avrg += val
        avrg /= len(vals)

        fd.write(str(filename.replace(".csv",""))+","+str(cday)+","+str(min_v)+","+str(max_v)+","+str(avrg)+"\n") 
        max_v = 0
        min_v = 100
        vals  = []
      cday = day

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

fd.close()
 
