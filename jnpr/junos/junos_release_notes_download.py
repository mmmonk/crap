#!/usr/bin/python -u

# $Id: 20120724$
# $Date: 2012-07-24 16:21:52$
# $Author: Marek Lukaszuk$

import urllib2
from urlparse import urljoin
import sgmllib
import re

jrels = ["9.3","10.0","10.2","10.4","11.1","11.2","11.3","11.4","12.1","12.2","12.3","12.4"]

class MyParser(sgmllib.SGMLParser):

  def parse(self, s):
    self.feed(s)
    self.close()

  def __init__(self, verbose=0):
    sgmllib.SGMLParser.__init__(self, verbose)
    self.hyperlinks = {}
    self.inside_a = ""

  def start_a(self, attributes):
    for name, value in attributes:
      if name == "href":
        if "junos-release-notes" in value:
          self.inside_a = value
  def handle_data(self, data):
    if not self.inside_a == "":
      self.hyperlinks[data] = self.inside_a

  def end_a(self):
    self.inside_a = ""

  def get_hyperlinks(self):
    return self.hyperlinks

opener = urllib2.build_opener()
urllib2.install_opener(opener)

releaselinks = {}

for rel in jrels:
  myparser = MyParser()
  relmain = "https://www.juniper.net/techpubs/en_US/junos"+str(rel)+"/information-products/pathway-pages/product/"+str(rel)+"/index.html"
  try:
    dat = urllib2.urlopen(relmain)
    text = dat.read()
  except:
    continue

  myparser.parse(text)
  links = myparser.get_hyperlinks()
  for link in links:
    jr = re.search("Release Notes(.*)",link,flags=re.I).group(1).strip().lower()
    jr.strip()
    fulllink = urljoin(relmain, links[link])
    filename = re.search("\/(junos-release-notes.+?pdf)",fulllink).group(1)
    if not jr == "":
      if not jr in filename:
        filename = re.sub("-\d+\S+?\.pdf","-"+str(jr)+".pdf",filename)
    try:
      open(filename,'r')
      print str(filename)+" exists"
      continue
    except:
      pass

    download = urllib2.urlopen(fulllink)
    dsize = int(download.info()['Content-Length'])
    try:
      gsize = 0
      dfile = open(filename,'w')
      while 1:
        data = download.read(32768)
        gsize += len(data)
        print "[?] Getting "+str(filename)+" : "+str(gsize/1024)+" kB ("+str(int((float(gsize)/(dsize))*100))+"%)\r",
        if not data:
          break
        dfile.write(data)
      print "[+] Download of "+str(filename)+" : "+str(gsize/1024)+" kB done"
    except:
      print "[!] error while downloading file: "+str(filename)

