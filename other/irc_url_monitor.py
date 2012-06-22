#!/usr/bin/env python

import sys
import os
import time
import smtplib

urlfile = "/home/case/.irssi/url"
urlhistory = "/home/case/.irssi/urlhistory"

if __name__ == '__main__':
  
  seenurls = {}
  newlinks = {}

  cleanolderthenthis = 30*24*3600 
  keepnumlimit = 5000

  oldlimit = int(time.time()) - cleanolderthenthis 
  if os.path.isfile(urlhistory) and os.stat(urlhistory).st_size > 0:
    for line in open(urlhistory,'r').readlines():
      (url,ts) = line.split()
      if ts > oldlimit:
        seenurls[url] = ts 

  if os.path.isfile(urlfile) and os.stat(urlfile).st_size > 0:
    for line in open(urlfile,'r').readlines(): 
      line = line.strip()
      line = line.strip(",.")
      linea = line.split()
      
      if not seenurls.has_key(linea[9]):
        newlinks[linea[9]] = linea[8]
      
      seenurls[linea[9]] = int(time.time())
    
    if len(newlinks) > 0:
    
      msg = "From: irssi@monkey.geeks.pl\nTo: m.lukaszuk@gmail.com\nSubject: irssi links from "+(time.strftime("%Y/%m/%d %H:%M:%S",time.localtime()))+"\n\n" 
      for link,channel in sorted(newlinks.items(), key=lambda x: x[0].replace("//www.","",1).split(":")[1]):
        msg += link+" "+channel+"\n"
      
      smtpObj = smtplib.SMTP("127.0.0.1")
      smtpObj.sendmail('m.lukaszuk@gmail.com','m.lukaszuk@gmail.com',msg)
      
      fd = open(urlhistory,'w')
      i = 0 
      for link,ts in sorted(seenurls.items(), key=lambda x: x[1], reverse=True):
        fd.write(link+" "+str(ts)+"\n")
        i += 1
        if i >= keepnumlimit:
          break
      fd.close()
      
      os.unlink(urlfile)
