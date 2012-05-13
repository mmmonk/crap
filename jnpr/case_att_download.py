#!/usr/bin/python

from cookielib import CookieJar
from urllib import urlencode,unquote
import urllib2 
from sgmllib import SGMLParser 
import sys
import os
import re

conffile = '/home/case/.nsmauth.conf'
maindir = "/home/case/store/jj/"
urlcm = "https://tools.online.juniper.net/cm/"

not_my_case = 0

# usage printout
def usage():
  print "\nUsage: "+str(sys.argv[0])+" Case-IDCa-seID [n]\n\
\n\
If n is set then the script will download the files to a temp folder.\n"
  sys.exit(1)

try:
  caseid = sys.argv[1]
except:
  usage()

try:
  if sys.argv[2]:
    not_my_case = 1 
except:
  pass

if not re.match("^\d{4}-\d{4}-\d{4}$",caseid):
  usage()

def LoadConf(filename):
  '''
  This loads the configuration settings from a file
  the syntax of the file looks like:
  attributename = attributevalue
  '''
  global confvar

  confvar = {} 
  try:
    conf = open(filename,'r')
  except:
    print "error during conf file read: "+str(filename)
    sys.exit(1)

  line = conf.readline()

  while line:
    conft = line.replace('\n','').split("=")
    confvar[conft[0]] = conft[1]
    line = conf.readline() 

class LoginForm(SGMLParser):
  '''
  This class analyses the Login form
  '''
  def parse(self, s):
    self.feed(s)
    self.close()

  def __init__(self, verbose = 0):
    SGMLParser.__init__(self, verbose)
    self.form = {} 
    self.inside_auth_form = 0

  def do_input(self, attributes):
    if self.inside_auth_form == 1:
      if 'hidden' in attributes[0]:
        self.form[attributes[1][1]] = attributes[2][1] 

  def start_form(self, attributes):
    for name, value in attributes:
      if name == "name" and value == "Login":
        self.inside_auth_form = 1
        break

  def end_form(self):
    self.inside_auth_form = 0 

  def get_form(self):
    return self.form


class CaseForm(SGMLParser):
  '''
  This class analyses the Case search form
  '''
  def parse(self, s):
    self.feed(s)
    self.close()

  def __init__(self, verbose = 0):
    SGMLParser.__init__(self, verbose)
    self.form = {} 
    self.inside_form = 0

  def do_input(self, attributes):
    if self.inside_form == 1:
      if 'hidden' in attributes[0]:
        self.form[attributes[1][1]] = attributes[2][1] 

  def start_form(self, attributes):
    for name, value in attributes:
      if name == "name" and value == "Login":
        self.inside_form = 1
        break

  def end_form(self):
    self.inside_form = 0 

  def get_form(self):
    return self.form

class CaseDetailsForm(SGMLParser):
  '''
  This class analyses the Case details form
  '''
  def parse(self, s):
    self.feed(s)
    self.close()

  def __init__(self, verbose = 0):
    SGMLParser.__init__(self, verbose)
    self.form = {}
    self.inside_form = 0

  def do_input(self, attributes):
    if self.inside_form == 1:
      if 'hidden' in attributes[0]:
        self.form[attributes[1][1]] = attributes[2][1]

  def start_form(self, attributes):
    for name, value in attributes:
      if name == "name" and value == "case_results":
        self.inside_form = 1
        break

  def end_form(self):
    self.inside_form = 0

  def get_form(self):
    return self.form

class CaseAttachForm(SGMLParser):
  '''
  This class analyses the Case attachments form
  '''
  def parse(self, s):
    self.feed(s)
    self.close()

  def __init__(self, verbose = 0):
    SGMLParser.__init__(self, verbose)
    self.form = {}
    self.inside_form = 0

  def do_input(self, attributes):
    if self.inside_form == 1:
      if 'hidden' in attributes[0]:
        self.form[attributes[1][1]] = attributes[2][1]

  def start_form(self, attributes):
    for name, value in attributes:
      if name == "name" and value == "case_detail":
        self.inside_form = 1
        break

  def end_form(self):
    self.inside_form = 0

  def get_form(self):
    return self.form
 
if __name__ == '__main__':
  LoadConf(conffile)

  cj = CookieJar()
  opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
  urllib2.install_opener(opener)
  try:
    dat = urllib2.urlopen(urlcm)
  except:
    print "[-] problem with connecting to the CM"
    sys.exit(1)

  print "[+] logging into the cm\r",
  try:
    fparser = LoginForm()
    fparser.parse(dat.read())
    form = fparser.get_form()
    form['USER'] = confvar['schemauser']
    form['PASSWORD'] = confvar['schemapass']
    dat = urllib2.urlopen(dat.geturl(),urlencode(form))
  except:
    print "[-] error while logging into cm"
    sys.exit(1)

  print "[+] searching for case "+str(caseid)+"\r",
  try:
    fparser = CaseForm()
    fparser.parse(dat.read())
    form = fparser.get_form()
    form['keyword'] = caseid
    form['fr'] = "5"
    dat = urllib2.urlopen(urlcm+"/case_results.jsp",urlencode(form))
  except:
    print "[-] error while searching for the case "+str(caseid)+"."
    sys.exit(1)

  print "[+] "+str(caseid)+": getting case details\r",
  try:
    text = dat.read()
    cid = re.search("href = \"javascript:setCid\(\'(.+?)\'",text)
    fparser = CaseDetailsForm()
    fparser.parse(text)
    form = fparser.get_form()
    form['cid'] = cid.group(1)
    dat = urllib2.urlopen(urlcm+"/case_detail.jsp",urlencode(form))
  except:
    print "[-] error while trying to get case "+str(caseid)+" details."
    sys.exit(1)

  print "[+] "+str(caseid)+": searching for case attachments\r",
  try:
    fparser = CaseAttachForm()
    fparser.parse(dat.read())
    form = fparser.get_form()
    dat = urllib2.urlopen(urlcm+"/case_attachments.jsp",urlencode(form))
  except:
    print "[-] error while searching for case "+str(caseid)+" attachments."
    sys.exit(1)

  text = dat.read()
  attach = re.findall("href=\"(AttachDown/.+?)\"",text)

  casedir = str(maindir)+"/"+str(caseid)+"/"
  if not_my_case == 1:
    casedir = str(maindir)+"/"+"temp/"+str(caseid)+"/" 

  print "[+] "+str(caseid)+": will download to "+str(casedir)

  for att in attach:
    filename = re.search("AttachDown/(.+?)\?OBJID = (.+?)\&",att)
    
    if not os.path.exists(casedir):
      os.makedirs(casedir)

    caseatt = str(filename.group(2))+"_"+str(filename.group(1))
    caseatt = re.sub("%3D","",caseatt)
    exists = 0
    try:
      save = open(casedir+caseatt,"r")
      save.close()
      exists = 1
    except:
      pass

    if exists == 0:
      att = urllib2.urlopen(urlcm+att)
      
      csize = 0
      try:
        save = open(casedir+caseatt,"w")
        while 1:
          data = att.read(102400)
          csize = csize + len(data)
          print "[+] Downloading "+str(caseatt)+" : "+str(csize/1024)+" Kbytes\r",
          if not data:
            break
          save.write(data)
        save.close()
        print "[+] Download of "+str(caseatt)+" size:"+str(csize/1024)+" Kbytes completed"
      except:
        os.unlink(casedir+caseatt)
        print "[-] error while downloading file: "+str(caseatt)
    else:
      print "[+] Attachment already exists: "+str(caseatt)

