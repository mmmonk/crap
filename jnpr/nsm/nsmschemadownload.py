#!/usr/bin/python

# $Id$

import cookielib
import urllib
import urllib2 
import sgmllib 
import sys

conffile='/home/case/.nsmauth.conf'

def LoadConf(filename):

  global confvar

  confvar = {} 
  try:
    conf=open(filename,'r')
  except:
    print "error during conf read"
    sys.exit(1)

  line = conf.readline()

  while line:
    conft = line.replace('\n','').split("=")
    confvar[conft[0]]=conft[1]
    line = conf.readline() 


class FormParser(sgmllib.SGMLParser):
  "A simple parser class."

  def parse(self, s):
    "Parse the given string 's'."
    self.feed(s)
    self.close()

  def __init__(self, verbose=0):
    sgmllib.SGMLParser.__init__(self, verbose)
    self.form = {} 
    self.inside_auth_form = 0

  def do_input(self, attributes):
    if self.inside_auth_form == 1:
      if 'hidden' in attributes[0]:
        self.form[attributes[1][1]]=attributes[2][1] 

  def start_form(self, attributes):
    for name, value in attributes:
      if name == "name" and value == "Login":
        self.inside_auth_form=1
        break

  def end_form(self):
    self.inside_auth_form=0    

  def get_form(self):
    return self.form

LoadConf(conffile)

url=confvar['schemalink']

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

dat = urllib2.urlopen(url)
parser = FormParser()
parser.parse(dat.read())

form = parser.get_form()
form['USER']=confvar['schemauser']
form['PASSWORD']=confvar['schemapass']
params = urllib.urlencode(form)
dat2 = urllib2.urlopen(dat.geturl(),params)
dat3 = urllib2.urlopen(dat2.geturl()) 
print dat3.info()['Last-Modified']+"\n"+dat3.info()['Content-Length']
