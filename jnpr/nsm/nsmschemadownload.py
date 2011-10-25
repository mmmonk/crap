#!/usr/bin/python

# $Id$

import time
import cookielib
import urllib
import urllib2 
import sgmllib 
import sys
import os
import re
from subprocess import Popen,PIPE 
from stat import *

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
maindir=confvar['nsmdiffdir']+'/schema'
email=confvar['nsmdiffdir']+"/.tosend"

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


# this was hit when there was a problem with the backend connection
httpok = 1
try:
  mdate = dat3.info()['Last-Modified']
  size = int(dat3.info()['Content-Length'])
except:
  httpok = 0

newschema = 0

try:
  timestampfile = open(maindir+'/schemainfo.txt','r')
  mdate_s = timestampfile.readline()
  if mdate != mdate_s.replace('\n',''):
    newschema = 1

  size_s = timestampfile.readline()
  if size != int(size_s.replace('\n','')):
    if newschema == 0:
      print "same timestamp different size - please check"
  else:
    if newschema == 1:
      print "same size different timestamp - please check"
except:
  newschema = 1

if newschema == 1 and httpok == 1:

  # below converts the time format we get from the Last-Modified field to a nicer looking string
  # Thu, 25 Nov 2010 03:21:25 GMT
  asctime = time.strftime("%Y%m%d_%H%M%S",time.strptime(mdate,"%a, %d %b %Y %H:%M:%S %Z"))

  schamefilename = maindir+"/schema_"+asctime+".tgz"

  chunk = 512000 

  try:
    schema = open(schamefilename,'r')
    print "file: "+schamefilename+" already exists"
    sys.exit(1)
  except:
    pass

  try:
    schema = open(schamefilename,'w')

    while 1:
      data = dat3.read(chunk)
      if not data:
        break
      schema.write(data)
  except:
    os.unlink(schamefilename)
    print "error while downloading schema"
    sys.exit(1)

  schema.close()

  timestampfile = open(maindir+'/schemainfo.txt','w')
  timestampfile.write(mdate+'\n'+str(size)+'\n')
  timestampfile.close()

  pipe = Popen("/bin/tar -zxOf "+maindir+"/schema_"+asctime+".tgz svn.log | /bin/grep 'revision='",shell=True, bufsize=512, stdout=PIPE).stdout
  revpattern = re.compile("\"[0-9]+\"")
  version = re.findall(revpattern,pipe.readline())[0]
  pipe.close()

  version = version.replace('"','')

  os.unlink(maindir+"/schema_"+asctime+".tgz")

  emailtxt = "From: "+confvar['emailfrom']+" \n\
To: "+confvar['emailto']+" \n\
Subject: [schemamonitor] New schema version "+version+" from "+mdate+" \n\n\n\
You can download it from here:\n\
ftp://172.30.73.133/nsmdiff_and_stuff/schema/schema_"+version+".tgz\n\
The file size is: "+str(size)+"\n\
The release notes information can be probably downloaded from here:\n\
http://kb.juniper.net/library/CUSTOMERSERVICE/GLOBAL_JTAC/technotes/DMI_Schema_v"+version+".pdf\n\n\
--\nThis email was created by a very intelligent script\nAll flames/complaints will go to /dev/null\n"

  try:
    open(email+"/schema_"+str(int(time.time())),'w').write(emailtxt)
  except:
    print emailtxt 
