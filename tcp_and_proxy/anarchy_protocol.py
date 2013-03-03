#!/usr/bin/env python

# $Id: 20130303$
# $Date: 2013-03-03 21:46:39$
# $Author: Marek Lukaszuk$

# anarchy protocol aka stateless protocol ;)

import sys
import os
import time
import struct

# TODO
# protocol my somehow keep track of a session but it can't relay on any src addressesa
# SYN "packets" should allow for exchange of DH (suffciently big - in the data part)
# that will be used for xoring over the transfered data.
# There should be a two byte session id, for each session.

class anarchy():

  def __init__(self, logts=True, maxlen=1300, keepalivetime = 0.5):
    self.mpid = os.getpid()
    self.logts = logts
    self.maxlen = maxlen
    self.keepalivetime = keepalivetime
    self.seq = 0
    self.ack = 0
    self.sent = dict() # this will be used by the client to make sure it keeps track of send packets
    self.headfmt = "BBBH" # TODO
    self.headsize = struct.calcsize(self.headfmt)
    self.sessid = 0

  def log(self, msg):
    # internal logging function
    try:
      txt="["+str(self.mpid)+"->"+str(self.chpid)+"] "+str(msg)
    except:
      txt="["+str(self.mpid)+"] "+str(msg)

    if self.logts == True:
      txt = time.asctime(time.localtime(time.time()))+" "+txt

    sys.stderr.write(txt+"\n")

  def dechead(self, head):
    # TODO
    pass

  def enchead(self, syn=0, fin=0, keepalive=0, moredata=0):
    # header:
    # session id = 2 bytes (first bit indicates if there is more data)
    # seq = 2 bytes
    # size = 2 bytes
    # TODO
    return ""

  def decflags(self, flags):
    return list(bin(int(flags)).replace("0b",""))

  def encflags(self, flags):
    flags = [ str(d) for d in flags]
    return int("".join(flags),2)

  def transform(self, data):
    return data


# TODO a lot below
class aserver(anarchy):
  # server class

  def __init__(self, lserver="127.0.0.1", lport=22):
    self.lserver = lserver
    self.lport = lport

class aclient(anarchy):
  # server class
  def __init__(self):
    pass
