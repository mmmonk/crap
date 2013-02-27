#!/usr/bin/env python

# $Id: 20130227$
# $Date: 2013-02-27 14:23:18$
# $Author: Marek Lukaszuk$

import sys
import os
import urllib2
import re
import pickle

ouidat = "/tmp/oui_cache.dat"

def pon(oui,mac):
  # matching the mac to a vendor
  a ="".join(re.findall("[0-9a-f]",mac.lower()))[:6]
  print str(a)+" - "+str(oui[a])

def refreshOUIdata(ouidat):
  # download new OUI data from a link and pickle it 
  ouiurl = "http://standards.ieee.org/develop/regauth/oui/oui.txt"
  
  oui = dict()
  for line in urllib2.urlopen(ouiurl).readlines():
    if '(hex)' in line:
      a = line.split()
      b = list()
      oui[a[0].replace("-","").lower()]=" ".join(a[2:])
  
  fd = open(ouidat,"wb")
  p = pickle.Pickler(fd,protocol=2)
  p.dump(oui)
  fd.close()

def loadOUI(ouidat):
  # load pickled OUI data from file
  fd = open(ouidat,"rb")
  p = pickle.Unpickler(fd)
  return p.load()
  
oui = dict()

if not os.path.isfile(ouidat): 
  refreshOUIdata(ouidat)

try:
  oui = loadOUI(ouidat)
except:
  refreshOUIdata(ouidat)
  oui = loadOUI(ouidat)

if len(sys.argv) == 1:
  for mac in sys.stdin.readlines():
    pon(oui,mac)
else:
  for mac in sys.argv[1:]:
    pon(oui,mac)
