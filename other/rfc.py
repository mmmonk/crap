#!/usr/bin/env python

# $Id: 20130305$
# $Date: 2013-03-05 22:36:30$
# $Author: Marek Lukaszuk$

import os
import sys
import time
import bz2
import urllib2
import argparse

class rfc():

  def __init__(self, rfcdir="~/.rfc", indextimeout=7):

    self.timeout = 3600*24*indextimeout # 7 days (by default)
    self.wdir = os.path.expanduser(rfcdir)
    self.idxurl = "https://www.ietf.org/download/rfc-index.txt"
    self.rfcurl = "https://tools.ietf.org/rfc/"
    self.idxdrf = "https://www.ietf.org/id/1id-index.txt"
    self.drfurl = "https://www.ietf.org/id/"

    if not os.path.exists(self.wdir):
      os.mkdir(self.wdir,0700)

  def fetchrfc(self,query,force=False):
    # this will fetch the given rfc
    if not os.path.isfile(self.wdir+os.sep+"rfc"+query+".bz2") or force:
      rfc = urllib2.urlopen(self.rfcurl+"rfc"+query+".txt")
      fd = bz2.BZ2File(self.wdir+os.sep+"rfc"+query+".bz2","wb")
      fd.write(rfc.read())
      fd.close()

  def fetchdraft(self,query,force=False):
    # this will fetch the given draft
    if not os.path.isfile(self.wdir+os.sep+query+".bz2") or force:
      rfc = urllib2.urlopen(self.drfurl+query)
      fd = bz2.BZ2File(self.wdir+os.sep+query+".bz2","wb")
      fd.write(rfc.read())
      fd.close()

  def fetchidx(self,idxfd,url,force=False):
    # this will fetch the rfc index
    try:
      mtime = int(time.time()-os.stat(idxfd).st_mtime)
    except OSError:
      mtime = self.timeout + 1

    if mtime > self.timeout or force:
      idx = urllib2.urlopen(url)
      fd = bz2.BZ2File(idxfd,"wb")
      fd.write(idx.read())
      fd.close()

  def query(self,s,force=False):

    # query type

    if s.isdigit():
      # rfc
      self.fetchrfc(s,force)
      return(bz2.BZ2File(self.wdir+os.sep+"rfc"+s+".bz2").read())

    elif "draft-" in s and ".txt" in s:
      # draft
      self.fetchdraft(s,force)
      return(bz2.BZ2File(self.wdir+os.sep+s+".bz2").read())

    else:
      out = ""

      # search through the RFC index
      self.fetchidx(self.wdir+os.sep+"rfc-index.bz2",self.idxurl,force)
      title = ""
      for line in bz2.BZ2File(self.wdir+os.sep+"rfc-index.bz2").readlines():
        if line == "\n":
          if "Status:" in title and s.lower() in title.lower():
            out += title+"\n"
          title = ""
        else:
          title += line.strip()+" "

      # search through the draft index
      self.fetchidx(self.wdir+os.sep+"1id-index.bz2",self.idxdrf,force)
      title = ""
      for line in bz2.BZ2File(self.wdir+os.sep+"1id-index.bz2").readlines():
        if line == "\n":
          if "draft-" in title and s.lower() in title.lower():
            out += title+"\n"
          title = ""
        else:
          title += line.strip()+" "

      return(out)

# a helper function
def query(s,f=False):
  r = rfc()
  return r.query(s,f)

if __name__ == "__main__":

  p = argparse.ArgumentParser(description='rfc search tool')
  p.add_argument("query",help="either an RFC number, a full file name of an IETF draft or a string to search in the RFCs and drafts titles")
  p.add_argument("-f",action='store_true',help="force redownload of either the index or the spcific item")
  #p.add_argument("-p",action='store_true',help="fetch pdf version if possible") # TODO
  args = p.parse_args()

  print query(args.query,args.f)

