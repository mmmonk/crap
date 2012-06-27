#!/usr/bin/env python

import sys
import operator
import random
from decimal import *
from base64 import *

getcontext().prec = 1000 

# https://en.wikipedia.org/wiki/Lagrange_polynomial
# this is a special case in which the Lagrange L(x) 
# function is actually L(0)

def result(points):
  total = Decimal(0)
  k = len(points)
  for i in xrange(k):
    l = Decimal(1) 
    for j in xrange(k):
      if j != i:
        l *= (Decimal(0) - Decimal(points[j][0]))/(Decimal(points[i][0]) - Decimal(points[j][0]))
   
    l *= Decimal(points[i][1]) 
    total += l

  return total

def usage():
  print sys.argv[0]+" <options> \n\n\
      Usage:\n\
      -h      - this screen,\n\
      -e msg  - generate secrets for msg,\n\
      -d      - recover secret based on the data in file (-f),\n\
      -f file - file to either write secrets or read them,\n\
      -a num  - overall number of secrets,\n\
      -r num  - required number of secrets,\n\
      "

if __name__ == "__main__":

  i = 1
  maxargv = len(sys.argv)
  
  opt_enc = ""
  opt_dec = 0
  opt_fd = ""
  opt_all = 0
  opt_req = 0

  try:
    while 1:
      
      if i >= maxargv:
        break

      arg = sys.argv[i]

      if arg == "-h":
        usage()
      elif arg == "-e":
        i += 1
        if i >= maxargv:
          sys.exit(1)
        opt_enc = sys.argv[i]+" "
      elif arg == "-d":
        opt_dec = 1
      elif arg == "-f":
        i += 1
        if i >= maxargv:
          sys.exit(1)
        opt_fd = sys.argv[i]
      elif arg == "-a":
        i += 1
        if i >= maxargv:
          sys.exit(1)
        opt_all = int(sys.argv[i])
      elif arg == "-r":
        i += 1
        if i >= maxargv:
          sys.exit(1)
        opt_req = int(sys.argv[i])
      else:
        sys.exit(1)
      i += 1
  except:
    usage()
    sys.exit(1)

  if not opt_enc == "":

    xv = []
    a = int(opt_enc.encode('hex'),16)
    xv.append(a)
    
    for i in xrange(opt_req-1):
      xv.append(random.randint(-1*a,a))

    for x in xrange(1,opt_all+1):
      y = xv[0]
      for i in xrange(1,len(xv)):
        y += xv[i]*(x**i)

      line = str(x)+":"+b32encode(str(y))
      if not opt_fd == "":
        try:
          open(opt_fd,"w").write(line+"\n")
        except IOError:
          print "problem with writing to file: "+str(opt_fd)
          sys.exit(1)
      else:
        print line
     
  elif opt_dec == 1 and not opt_fd == "":
    try:
      lines = [ line.strip().split(":") for line in open(opt_fd).readlines()]
    except IOError:
      print "file "+str(opt_fd)+" could not be read !"
      usage()
      sys.exit(1)
    points = [ (int(x),int(b32decode(y))) for x,y in lines]

    out = hex(int(result(points))).replace("0x","").replace("L","")
    print out.decode('hex')

  else:
    usage()
