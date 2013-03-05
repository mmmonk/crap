#!/usr/bin/env python

# $Id: 20130305$
# $Date: 2013-03-05 17:44:26$
# $Author: Marek Lukaszuk$

import os
import sys
import time
import bz2
import urllib2
import argparse

class rfc():

  def __init__(self, rfcdir="~/.rfc", indextimeout=7):

    self.timeout = 3600*24*indextimeout
    self.wdir = os.path.expanduser(rfcdir)
    self.idxurl = "https://www.ietf.org/download/rfc-index.txt"
    self.rfcurl = "https://tools.ietf.org/rfc/"

    if not os.path.exists(self.wdir):
      os.mkdir(self.wdir,0700)

  def fetch(self,query,force=False):

    # this will fetch the given rfc

    if not os.path.isfile(self.wdir+os.sep+"rfc"+query+".bz2") or force:
      rfc = urllib2.urlopen(self.rfcurl+"rfc"+query+".txt")
      fd = bz2.BZ2File(self.wdir+os.sep+"rfc"+query+".bz2","wb")
      fd.write(rfc.read())
      fd.close()

  def fetchidx(self,force=False):

    # this will fetch the rfc index

    try:
      mtime = int(time.time()-os.stat(self.wdir+os.sep+"rfc-index.bz2").st_mtime)
    except OSError:
      mtime = self.timeout + 1

    if mtime > self.timeout or force:
      idx = urllib2.urlopen(self.idxurl)
      fd = bz2.BZ2File(self.wdir+os.sep+"rfc-index.bz2","wb")
      fd.write(idx.read())
      fd.close()

  def query(self,s,force=False):

    # query type

    if s.isdigit():
      # printing given rfc
      self.fetch(s,force)
      return(bz2.BZ2File(self.wdir+os.sep+"rfc"+s+".bz2").read())

    else:
      # search through the index
      self.fetchidx(force)
      title = ""
      out = ""
      for line in bz2.BZ2File(self.wdir+os.sep+"rfc-index.bz2").readlines():
        if line == "\n":
          if s.lower() in title.lower():
            out += title+"\n"
          title = ""
        else:
          title += line.strip()

      return(out)

# a helper function
def query(s,f=False):
  r = rfc()
  return r.query(s,f)

if __name__ == "__main__":

  p = argparse.ArgumentParser(description='rfc search tool')
  p.add_argument("query",help="either an RFC number or a string to find in the RFC title")
  p.add_argument("-f",action='store_true',help="force redownload of either specific RFC or RFC index")
  p.add_argument("-p",action='store_true',help="fetch pdf version if possible") # TODO
  args = p.parse_args()

  if sys.stdout.isatty(): # TODO: add pager
    print query(args.query,args.f)

  else:
    print query(args.query,args.f)
