#!/usr/bin/env python

'''
$Id: 20130315$
$Date: 2013-03-15 11:58:10$
$Author: Marek Lukaszuk$

this script will search and download the given draft and rfc and store
a compress copy (using bz2) in the home folder
'''

import os
import sys
import time
import bz2
import urllib2
import argparse

class rfc():

  def __init__(self, rfcdir="~/.rfc", indextimeout=7):
    '''
    indextimeout - how often (in days) to refresh the index
    '''
    self.timeout = 3600*24*indextimeout # 7 days (by default)
    self.wdir = os.path.expanduser(rfcdir)
    self.idxurl = "https://tools.ietf.org/rfc/rfc-index.txt"
    self.rfcurl = "https://tools.ietf.org/rfc/"
    self.idxdrf = "https://tools.ietf.org/id/1id-index.txt"
    self.drfurl = "https://tools.ietf.org/id/"
    self.idxirt = "https://tools.ietf.org/id/all_id2.txt"

    if not os.path.exists(self.wdir):
      os.mkdir(self.wdir,0700)

  def fetchrfc(self,query,force=False):
    '''
    this will fetch the given rfc from https://tools.ietf.org/rfc/
    '''
    if not os.path.isfile(self.wdir+os.sep+"rfc"+query+".bz2") or force:
      rfc = urllib2.urlopen(self.rfcurl+"rfc"+query+".txt")
      fd = bz2.BZ2File(self.wdir+os.sep+"rfc"+query+".bz2","wb")
      fd.write(rfc.read())
      fd.close()

  def fetchdraft(self,query,force=False):
    '''
    this will fetch the given draft from https://www.ietf.org/id/
    '''
    if not os.path.isfile(self.wdir+os.sep+query+".bz2") or force:
      rfc = urllib2.urlopen(self.drfurl+query)
      fd = bz2.BZ2File(self.wdir+os.sep+query+".bz2","wb")
      fd.write(rfc.read())
      fd.close()

  def fetchidx(self,idxfd,url,force=False):
    '''
    this will fetch the rfc index from https://tools.ietf.org/rfc/rfc-index.txt
    or a the draft index from https://tools.ietf.org/id/1id-index.txt
    or a complete list of drafts from https://tools.ietf.org/id/all_id2.txt
    '''
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
    '''
    based on the provided string it will do the magic(tm):
     if the string is a number if will show a give RFC
     if the string stars with "draft-" and ends with ".txt" it show you a given draft
     if it is anything else then it will search the rfc index and draft index
    '''
    if s.isdigit():
      # rfc
      try:
        self.fetchrfc(s,force)
        return(bz2.BZ2File(self.wdir+os.sep+"rfc"+s+".bz2").read())
      except:
        print "Error: downloading/saving RFC"
        sys.exit()

    elif s.startswith("draft-") and s.endswith(".txt"):
      # draft
      try:
        self.fetchdraft(s,force)
        return(bz2.BZ2File(self.wdir+os.sep+s+".bz2").read())
      except:
        print "Error: downloading/saving draft"
        sys.exit()

    else:
      out = ""

      # search through the RFC index
      try:
        self.fetchidx(self.wdir+os.sep+"rfc-index.bz2",self.idxurl,force)
      except:
        print "Error: downloading/saving RFC index"
        sys.exit()

      title = ""
      for line in bz2.BZ2File(self.wdir+os.sep+"rfc-index.bz2").readlines():
        if line == "\n":
          if "Status:" in title and s.lower() in title.lower():
            out += title+"\n"
          title = ""
        else:
          title += line.strip()+" "

      # search through the ietf draft index
      try:
        self.fetchidx(self.wdir+os.sep+"1id-index.bz2",self.idxdrf,force)
      except:
        print "Error: downloading/saving IETF index"
        sys.exit()
      title = ""
      for line in bz2.BZ2File(self.wdir+os.sep+"1id-index.bz2").readlines():
        if line == "\n":
          if "draft-" in title and s.lower() in title.lower():
            out += title+"\n"
          title = ""
        else:
          title += line.strip()+" "

      # search through the irtf draft index
      try:
        self.fetchidx(self.wdir+os.sep+"all_id2.bz2",self.idxirt,force)
      except:
        print "Error: downloading/saving IRTF index"
        sys.exit()
      for line in bz2.BZ2File(self.wdir+os.sep+"all_id2.bz2").readlines():
        if line[0] == "#":
          continue

        t = line.strip().split("\t")

        if "rfc" in t[2].lower():
          continue

        if not "irtf" in t[0].lower():
          continue

        if s.lower() in line.lower():
          out += "\""+t[13]+"\", "+t[2]+", "+t[5]+", "+t[6]+", <"+t[0]+".txt>\n"

      return(out)



def query(s,f=False):
  '''
  helper function for easier usage
  '''
  r = rfc()
  return r.query(s,f)

if __name__ == "__main__":

  p = argparse.ArgumentParser(description='rfc search tool')
  p.add_argument("query",help="either an RFC number, a full file name of an IETF draft or a string to search in the RFCs and drafts titles")
  p.add_argument("-f",action='store_true',help="force redownload of either the index or the spcific item")
  args = p.parse_args()

  try:
    print query(args.query,args.f)
  except IOError:
    pass
