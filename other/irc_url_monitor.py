#!/usr/bin/env python

import sys, os, time, smtplib

urlfile = "/home/case/.irssi/url"
urlhistory = "/home/case/.irssi/urlhistory"

if __name__ == '__main__':

  seenurls = {}
  newlinks = {}

  cleanolderthenthis = 60*24*3600
  keepnumlimit = 10000

  oldlimit = int(time.time()) - cleanolderthenthis
  if os.path.isfile(urlhistory) and os.stat(urlhistory).st_size > 0:
    data = open(urlhistory,'r').read().decode('bz2')
    for line in data.split("\n"):
      if len(line) > 5:
        (url,ts) = line.split()
        if ts > oldlimit:
          seenurls[url] = ts
    data = ""

  if os.path.isfile(urlfile) and os.stat(urlfile).st_size > 0:
    for line in open(urlfile,'r').readlines():
      line = line.strip()
      line = line.strip(",.")
      linea = line.split()

      if "://" not in linea[9]:
        continue

      if not seenurls.has_key(linea[9]):
        newlinks[linea[9]] = linea[8]+" "+linea[7]

      seenurls[linea[9]] = int(time.time())

    if len(newlinks) > 0:

      msg = "From: irssi@monkey.geeks.pl\nTo: m.lukaszuk@gmail.com\nSubject: irssi links from "+(time.strftime("%Y/%m/%d %H:%M:%S",time.localtime()))+"\n\n"
      for link,channel in sorted(newlinks.items(), key=lambda x: x[0].replace("//www.","//",1).split(":")[1]):
        msg += link+" "+channel+"\n"

      smtpObj = smtplib.SMTP("127.0.0.1")
      smtpObj.sendmail('m.lukaszuk@gmail.com','m.lukaszuk@gmail.com',msg)

      data = ""
      i = 0
      for link,ts in sorted(seenurls.items(), key = lambda x: x[1], reverse=True):
        data += link+" "+str(ts)+"\n"
        i += 1
        if i >= keepnumlimit:
          break

      fd = open(urlhistory,'w')
      fd.write(data.encode('bz2'))
      fd.close()

      os.unlink(urlfile)
