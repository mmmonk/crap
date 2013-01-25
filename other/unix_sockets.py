#!/usr/bin/env python

# $Id: 20130121$
# $Date: 2013-01-21 10:12:14$
# $Author: Marek Lukaszuk$

import sys
import os
import time
import socket
import select

def addts(data,user="",source=""):
  a = list()
  for l in data.split("\n"):
    if not l == "":
      a.append(str(time.time())+"|"+user+"|"+source+"|"+l.strip())

  return a

file1 = "console_test"
file2 = "console_test_out"

try:
  cons = socket.socket(socket.AF_UNIX)
  cons.connect(file1)
  cons.setblocking(False)

  out = socket.socket(socket.AF_UNIX)
  out.bind(file2)
  out.listen(1)
  out.setblocking(False)

  while True:
    read,[],[] = select.select([out,cons],[],[],30)

    if out in read:
      mgt,addr = out.accept()

      try:
        (user,source) = mgt.recv(4096).strip().split()
      except:
        print sys.exc_info()
        user = ""
        source = ""

      while True:
        toread,[],[] = select.select([cons,mgt],[],[],30)
        [],towrite,[] = select.select([],[cons,mgt],[],30)

        if mgt in toread and cons in towrite:
          data = mgt.recv(4096)
          if len(data) == 0:
            break
          else:
            print "\n".join(addts(data,user,source))
            cons.send(data)

        elif cons in toread and mgt in towrite:
          data = cons.recv(4096)
          if len(data) == 0:
            break
          else:
            print "\n".join(addts(data,user,source))
            mgt.send(data)

    if cons in read:
      data = cons.read(4096)
      print "\n".join(addts(data))

except:
  print sys.exc_info()
  os.unlink(file2)
