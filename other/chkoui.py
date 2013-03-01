#!/usr/bin/env python

# $Id: 20130301$
# $Date: 2013-03-01 10:13:00$
# $Author: Marek Lukaszuk$

import sys
import os
import urllib2
import re
import pickle
import bz2
import time

class checkOUI():

  def __init__(self, db="/tmp/oui_cache.dat"):
    self.ouidat = os.path.dirname(db)+os.sep+os.environ['USER']+"_"+os.path.basename(db)
    self.url = "http://standards.ieee.org/develop/regauth/oui/oui.txt"
    self.oui = dict()

    if not os.path.isfile(self.ouidat):
      self.downloadDB()

    # refresh the db after a month (30 days)
    if int(time.time())-os.stat(self.ouidat)[8] > 2592000:
      self.downloadDB(refresh=True)

    try:
      self.loadDB()
    except:
      self.downloadDB()
      self.loadDB()


  def check(self,mac):
    # matching the mac to a vendor
    a ="".join(re.findall("[0-9a-f]",mac.lower()))[:6]
    if self.oui.has_key(a):
      return str(a)+" - "+str(self.oui[a])
    return str(a)+" - unknown"

  def downloadDB(self, refresh=False):
    # download new OUI data from a link and pickle it

    print "[+] downloading the oui database"
    oui = dict()
    fail = False
    try:
      for line in urllib2.urlopen(self.url).readlines():
        if '(hex)' in line:
          a = line.split()
          b = list()
          oui[a[0].replace("-","").lower()]=" ".join(a[2:])
    except:
      print "[-] error while downloading the file"
      fail = True
      if refresh == False:
        sys.exit()

    if fail == False:
      try:
        fd = bz2.BZ2File(self.ouidat+"tmp","wb")
        pickle.Pickler(fd,protocol=2).dump(oui)
        fd.close()
      except:
        print "[-] error while saving file"
        fail = True
        if refresh == False:
          sys.exit()

    if fail == False:
      os.rename(self.ouidat+"tmp",self.ouidat)

  def loadDB(self):
    # load pickled OUI data from file
    fd = bz2.BZ2File(self.ouidat,"rb")
    self.oui = pickle.Unpickler(fd).load()
    fd.close()

if __name__ == "__main__":

  oui = checkOUI()

  if len(sys.argv) == 1:
    for mac in sys.stdin.readlines():
      print oui.check(mac)
  else:
    for mac in sys.argv[1:]:
      print oui.check(mac)
