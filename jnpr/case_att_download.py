#!/usr/bin/python

import time
from cookielib import CookieJar
from urllib import urlencode
import urllib2 
import sgmllib 
import sys
import os
import re
#import stat

conffile='/home/case/.nsmauth.conf'
maindir="/home/case/store/jj/"
caseid=sys.argv[1]

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


class LoginForm(sgmllib.SGMLParser):
  def parse(self, s):
    self.feed(s)
    self.close()

  def __init__(self, verbose=0):
    sgmllib.SGMLParser.__init__(self, verbose)
    self.form = {} 
    self.inside_auth_form=0

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


class CaseForm(sgmllib.SGMLParser):
  def parse(self, s):
    self.feed(s)
    self.close()

  def __init__(self, verbose=0):
    sgmllib.SGMLParser.__init__(self, verbose)
    self.form = {} 
    self.inside_form=0

  def do_input(self, attributes):
    if self.inside_form == 1:
      if 'hidden' in attributes[0]:
        self.form[attributes[1][1]]=attributes[2][1] 

  def start_form(self, attributes):
    for name, value in attributes:
      if name == "name" and value == "Login":
        self.inside_form=1
        break

  def end_form(self):
    self.inside_form=0 

  def get_form(self):
    return self.form

class CaseDetailsForm(sgmllib.SGMLParser):
  def parse(self, s):
    self.feed(s)
    self.close()

  def __init__(self, verbose=0):
    sgmllib.SGMLParser.__init__(self, verbose)
    self.form = {}
    self.inside_form=0

  def do_input(self, attributes):
    if self.inside_form == 1:
      if 'hidden' in attributes[0]:
        self.form[attributes[1][1]]=attributes[2][1]

  def start_form(self, attributes):
    for name, value in attributes:
      if name == "name" and value == "case_results":
        self.inside_form=1
        break

  def end_form(self):
    self.inside_form=0

  def get_form(self):
    return self.form

class CaseAttachForm(sgmllib.SGMLParser):
  def parse(self, s):
    self.feed(s)
    self.close()

  def __init__(self, verbose=0):
    sgmllib.SGMLParser.__init__(self, verbose)
    self.form = {}
    self.inside_form=0

  def do_input(self, attributes):
    if self.inside_form == 1:
      if 'hidden' in attributes[0]:
        self.form[attributes[1][1]]=attributes[2][1]

  def start_form(self, attributes):
    for name, value in attributes:
      if name == "name" and value == "case_detail":
        self.inside_form=1
        break

  def end_form(self):
    self.inside_form=0

  def get_form(self):
    return self.form
  
LoadConf(conffile)

cj = CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
urllib2.install_opener(opener)

dat = urllib2.urlopen("https://tools.online.juniper.net/cm/")

fparser = LoginForm()
fparser.parse(dat.read())
form = fparser.get_form()
form['USER']=confvar['schemauser']
form['PASSWORD']=confvar['schemapass']
dat = urllib2.urlopen(dat.geturl(),urlencode(form))

fparser = CaseForm()
fparser.parse(dat.read())
form = fparser.get_form()
form['keyword']=caseid
form['fr']="5"
dat = urllib2.urlopen("https://tools.online.juniper.net/cm/case_results.jsp",urlencode(form))

text = dat.read()
cid = re.search("href=\"javascript:setCid\(\'(.+?)\'",text)
fparser = CaseDetailsForm()
fparser.parse(text)
form = fparser.get_form()
form['cid']=cid.group(1)
dat = urllib2.urlopen("https://tools.online.juniper.net/cm/case_detail.jsp",urlencode(form))

fparser = CaseAttachForm()
fparser.parse(dat.read())
form = fparser.get_form()
dat = urllib2.urlopen("https://tools.online.juniper.net/cm/case_attachments.jsp",urlencode(form))

text = dat.read()
attach = re.findall("href=\"(AttachDown/.+?)\"",text)

for att in attach:
  filename = re.search("AttachDown/(.+?)\?OBJID=(.+?)\&",att)
  casedir = str(maindir)+"/"+str(caseid)+"/"
  if not os.path.exists(casedir):
    os.makedir(casedir)

  caseatt = casedir+str(filename.group(2))+"_"+str(filename.group(1))
  exists = 0
  try:
    save = open(caseatt,"r")
    save.close()
    exists = 1
  except:
    pass

  if exists == 0:
    att = urllib2.urlopen("https://tools.online.juniper.net/cm/"+att)
    
    csize = 0
    try:
      save = open(caseatt,"w")
      while 1:
        data = att.read(10000)
        csize = csize + len(data)
        print "[+] Downloading "+str(caseatt)+" : "+str(csize/1024)+" Kbytes\r",
        if not data:
          break
        save.write(data)
      save.close()
      print "[+] Download "+str(caseatt)+" size:"+str(csize/1024)+" Kbytes completed"
    except:
      os.unlink(caseatt)
      print "error while downloading file: "+str(caseatt)
  else:
    print "[+] Attachment already exists: "+str(caseatt)

