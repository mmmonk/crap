#!/usr/bin/env python

import sys

rfcdir = "/home/case/store/docs/ftp.ietf.org/rfc/"
rfcindex = rfcdir+"/rfc-index"

if len(sys.argv) < 2:
  print "usage: "+sys.argv[0]+" (pattern_to_search_for|rfc_number)"
  sys.exit(1)

query = sys.argv[1]

if query.isdigit():
  try:
    print open(rfcdir+"/rfc"+query,"r").read()
  except:
    print "can't open rfc"+query

else:
  try:
    rfc = open(rfcindex,"r")
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

  
