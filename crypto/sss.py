#!/usr/bin/env python

# $Id: 20120722$
# $Date: 2012-07-22 13:49:06$
# $Author: Marek Lukaszuk$

import sys
import random
from decimal import *
from base64 import *

# if you have problems with the decryption, increase this value
getcontext().prec = 1000


def Lagrange_polynomial(points):
  '''
  input: array of tuples (x,y)
  We calculate here the constant that is present in the polynomial
  at the x^0. This constant is our secret. We use this:
  https://en.wikipedia.org/wiki/Lagrange_polynomial
  but in our case function is actually L(0)
  '''
  a = Decimal(0)
  k = len(points) # how many points we actually have
  for i in xrange(k): # this is for the y values
    l = Decimal(1)
    for j in xrange(k): # those are the x values
      if j != i: # l = (x0 - xj) / (xi - xj)
        l *= (Decimal(0) - Decimal(points[j][0]))/(Decimal(points[i][0]) - Decimal(points[j][0]))

    # multiply the previous l by yi
    l *= Decimal(points[i][1])
    a += l

  return a

def usage():
  print sys.argv[0]+" <options> \n\n\
  Usage:\n\n\
  This program implements in a very simple and basic way\n\
  Shamir's secret-sharing scheme:\n\
  https://en.wikipedia.org/wiki/Shamir%27s_Secret_Sharing\n\n\
  -h      - this screen,\n\
  -e msg  - generate secrets for msg,\n\
  -d      - recover secret based on the data in file (-f),\n\
  -f file - file to either write secrets or read them,\n\
  -a num  - overall number of secrets (not less then -r),\n\
  -r num  - required number of secrets (min 2),\n"

if __name__ == "__main__":

  i = 1
  maxargv = len(sys.argv)

  opt_enc = ""
  opt_dec = 0
  opt_fd = ""
  opt_all = 0
  opt_req = 0

  # arguments processing
  try:
    while 1:

      if i >= maxargv:
        break

      arg = sys.argv[i]

      if arg == "-h": # help/usage
        usage()
      elif arg == "-e": # encode
        i += 1
        if i >= maxargv:
          sys.exit(1)
        opt_enc = sys.argv[i]+" "
      elif arg == "-d": # decode
        opt_dec = 1
      elif arg == "-f": # filename
        i += 1
        if i >= maxargv:
          sys.exit(1)
        opt_fd = sys.argv[i]
      elif arg == "-a": # all shares
        i += 1
        if i >= maxargv:
          sys.exit(1)
        opt_all = int(sys.argv[i])
      elif arg == "-r": # required shares
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

  if not opt_enc == "" and opt_req > 1: # we are encoding it here

    if opt_all < opt_req:
      opt_all = opt_req

    xv = []
    a = int(opt_enc.encode('hex'),16)
    xv.append(a) # this is our secret, value a*x^0

    # randomly generate all other constansts for polynomial
    # the range for the other contstant is (-2*a,2*a)
    for i in xrange(opt_req-1):
      xv.append(random.randint(0-(2*a),(2*a)))

    # randomly pick unique x to calculate f(x)
    # we can't pick 0 here, because this is our secret
    xseen = {}
    for i in xrange(1,opt_all+1):
      while 1:
        try:
          x = random.randint(1,1000000000000)
          if xseen[x] == 0:
            pass
        except KeyError:
          break

      # counting f(x)=y
      y = xv[0]
      for j in xrange(1,len(xv)):
        y += xv[j]*(x**j)

      # text output, convert y to base32
      line = b32encode(str(x)+":"+str(y))
      if not opt_fd == "": # output to file
        try:
          open(opt_fd,"a").write(line+"\n")
        except IOError:
          print "problem with writing to file: "+str(opt_fd)
          sys.exit(1)
      else: # output to stdout
        print line

  elif opt_dec == 1 and not opt_fd == "": # decoding part
    try:
      # reading from a file
      # format:
      # x:base32(y)
      lines = [ b32decode(line.strip()).split(":") for line in open(opt_fd).readlines()]
    except IOError:
      print "file "+str(opt_fd)+" could not be read !"
      usage()
      sys.exit(1)

    # converting text to tuples (x,y)
    points = [ (int(x),int(y)) for x,y in lines]

    # coming up with the secret value
    out = hex(int(Lagrange_polynomial(points))).replace("0x","").replace("L","")
    print out.decode('hex')

  else: # something went wrong
    usage()
