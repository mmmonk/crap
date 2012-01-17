#!/usr/bin/env python

from subprocess import call,Popen,PIPE
from time import time
import os
import sys

rfcdir = "/home/case/store/rfc/"
maxtime = 3600*24*7;

wget = "/usr/bin/wget -t 3 -m -q -O "
bzip2 = "/bin/bzip2 -c"

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
    
    if not os.path.isfile(rfcdir+"/rfc"+query+".bz2"): 
      call(wget+" - https://tools.ietf.org/rfc/rfc"+query+".txt | "+bzip2+" > "+rfcdir+"/rfc"+query+".bz2", shell=True)
    print Popen(bzip2+" -d "+rfcdir+"/rfc"+query+".bz2", shell=True, stdout=PIPE).stdout.read()
  except:
    print "can't open rfc"+query

else:
  try:
    try:
      mtime = (int(time())-int(os.stat(rfcdir+"/rfc-index").st_mtime))/3600
    except OSError:
      mtime = maxtime+1;
    
    if mtime > maxtime:
      call(wget+rfcdir+"/rfc-index ftp://ftp.ietf.org/rfc/rfc-index",shell=True)
    
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

  
