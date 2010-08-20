#!/usr/bin/env python

# $Id$

from ftplib import FTP
import os
import time
import sys

MAINDIR = '/home/case/store/juniper/nsmdiff'
EMAIL = MAINDIR+"/"+".tosend"
SERVERRETRY = 5
SERVERRETRYTIME = 300

if __name__ == '__main__':

  serverretrycount = 0
  serverok = 0
  
  while serverok == 0:
    try:
      nsm = FTP('ftp.company.gov')
      nsm.login('user','pass')
      nsm.cwd('/tftpboot/ims')
      lst = nsm.nlst()
      serverok = 1
    except:
      serverretrycount += 1
      time.sleep(SERVERRETRYTIME)
      if serverretrycount >= SERVERRETRY:
        print "There were errors with the connection to the server\n"
        sys.exit(1)
  

  somethingnew = 0

  difftext = "From: <mlukaszuk@comapny.net> \n\
To: <mlukaszuk@comapny.net> \n\
Subject: [NSMDIFF] update from "+(time.strftime("%Y/%m/%d %H:%M:%S",time.localtime()))+"\n" 

  for ver in lst:
    if 'LGB' in ver:
      if not os.path.isdir(MAINDIR+"/"+ver):
        vlst=nsm.nlst(ver)
        for diff in vlst:
          if '_filediff' in diff:
            rsize = nsm.size(diff)
            os.mkdir(MAINDIR+"/"+ver)
            lsize = 0
            r1size = 0
            while not ((lsize == rsize)and(rsize == r1size)):
              nsm.retrbinary("RETR "+diff, open(MAINDIR+"/"+diff,'wb').write)
              r1size = nsm.size(diff)
              lsize = os.stat(MAINDIR+"/"+diff).st_size
              if not (r1size == rsize):
                time.sleep(30)

            difftext += "\n\nFixes in "+ver+"\n=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=-=\n"
            difftext += open(MAINDIR+"/"+diff,'r').read()
            somethingnew = 1

  nsm.quit()

  if somethingnew == 1:
    difftext += "--\nYour friendly automatic servant\nAll flames/complaints will go to /dev/null\n"
    try:
      open(EMAIL+"/diff"+str(int(time.time())),'w').write(difftext)
    except:
      print difftext

