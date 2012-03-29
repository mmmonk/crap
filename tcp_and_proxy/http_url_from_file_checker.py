#!/usr/bin/python

import httplib
import sys

proto = "http"
host = ""
baseurl = "/"

try: 
  (proto,undef,host,baseurl) = sys.argv[1].split("/",3)
  filename = sys.argv[2]  
except:
  print "Usage:"
  sys.exit(1)

if "https" in proto:
  con = httplib.HTTPSConnection(host)
else:
  con = httplib.HTTPConnection(host)

urls = open(filename).readlines()

for url in urls:
  url = url.rstrip()
  url = url.lstrip("./")
  con.request("HEAD","/"+baseurl+url)
  resp = con.getresponse()
  print "response:"+str(resp.status)+" request: "+proto+"//"+host+"/"+baseurl+url+" headers:"+str(resp.getheaders())
