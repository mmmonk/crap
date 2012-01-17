#!/usr/bin/env python

from subprocess import call
import sys
import os
import time

rfcdir = "/home/case/store/rfc/"

wget = "/usr/bin/wget"

if len(sys.argv) < 2:
  print "usage: "+sys.argv[0]+" (pattern_to_search_for|rfc_number)"
  sys.exit(1)

query = sys.argv[1]

try:
  os.mkdir(rfcdir,0700)
except:
  pass

if query.isdigit():
  try:
    try:
      print open(rfcdir+"/rfc"+query,"r").read()
    except IOError:
      call(wget+" -m -q -t 2 -O "+rfcdir+"/rfc"+query+" https://tools.ietf.org/rfc/rfc"+query+".txt", shell=True)
      print open(rfcdir+"/rfc"+query,"r").read()
  except:
    print "can't open rfc"+query

else:
  try:
    try:
      if (int(time.time())-int(os.stat(rfcdir+"/rfc-index").st_mtime))/3600 > 3600*24*7:
        call(wget+" -q -t 3 -O "+rfcdir+"/rfc-index ftp://ftp.ietf.org/rfc/rfc-index",shell=True)
    except OSError, e:
      call(wget+" -q -t 3 -O "+rfcdir+"/rfc-index ftp://ftp.ietf.org/rfc/rfc-index",shell=True)
    rfc = open(rfcdir+"/rfc-index","r")
  except:
    print "can't open rfc index"
    sys.exit(1)

  title = ""
  start = False
  line = 1

  while line:
    line = rfc.readline()

    if line == "\n":
      if " 0001 " in title:
        start = True

      if start == True and query.lower() in title:
        print title
      
      title = ""
    else:
      title += " "+line.strip().lower()

  
