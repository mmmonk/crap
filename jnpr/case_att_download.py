#!/usr/bin/python -u

from cookielib import CookieJar
from urllib import urlencode,unquote,quote
import urllib2 
from sgmllib import SGMLParser 
import sys
import os
import re
from time import sleep
from ftplib import FTP,error_perm

version = "20120521"

def usage():
  '''
  function printing usage/help information
  '''
  print "\nUsage: "+str(sys.argv[0])+" <options> Case-IDCa-seID\n\
\n\
Author: Marek Lukaszuk\n\
Version: "+str(version)+"\n\n\
Options:\n\
-d directory  directory where to download attachments,\n\
              inside that directory a directory with the case number will be created,\n\
-i regexp     (include) download or list only attachments which filenames match regexp,\n\
-e regexp     (exclude) skip attachments which filenames match regexp,\n\
-h            this help,\n\
-l            just list case attachments without downloading,\n\
-o            force overwrite of the files,\n\
-p pass       password used for the CM,\n\
-t            this will download attachments to a folder \"temp\"\n\
              in the destination folder (for cases that you just want to look at),\n\
-u user       user name used for the CM,\n\
\n\
You can define the user, password and the download directory in a file\n\
"+str(os.environ['HOME'])+"/.cm.conf\n\
which should look like this:\n\
cmuser=YOUR_USERNAME_FOR_CM\n\
cmpass=YOUR_PASSWORD_FOR_CM\n\
cmdir=THE_MAIN_DIRECTORY_WHERE_TO_DOWNLOAD_ATTACHMENTS\n\n\
By default this script will download all the attachments for a given case\n\
from case manager and from ftp server to the case directory inside current directory.\n\
Options -i (include) and -e (exclude) can be specified together. In that case first filenames\n\
will be matched against the include regexp and later against the exclude regexp.\n"
  sys.exit(1)

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
    print "[!] error during conf file read: "+str(filename)
    return

  line = conf.readline()

  while line:
    conft = line.replace(os.linesep,'').split("=")
    confvar[conft[0]] = conft[1]
    line = conf.readline() 

def progressindicator(sign):
  '''
  rotating sign, progress indicator
  '''
  if sign == "|":
    sign = "/"
  elif sign == "/":
    sign = "-"
  elif sign == "-":
    sign = "\\" 
  else:
    sign = "|"
  return sign

def ftpcallback(data):
  '''
  call back function used while getting data via ftplib
  '''
  global fcount, ftpfile, ftpprogind
  fcount+=len(data)
  ftpfile.write(data)
  ftpprogind = progressindicator(ftpprogind)
  print "["+str(ftpprogind)+"] Getting "+str(ftpatt)+" "+str(fcount/1024)+" kB ("+str(int((float(fcount)/fsize)*100))+"%)\r",


def ftpcheck(caseid,casedir,ftp):
  '''
  this checks for files inside the specific folder
  of the ftp server, it also makes sure not to overwrite files
  '''
  ftplist = ftp.nlst()
  print "[+] "+str(caseid)+": found "+str(len(ftplist))+" file(s) in "+str(ftp.pwd()) 
  for filename in ftplist:
    # downloading attachments
    if not opt_incl == "":
      if not re.search(opt_incl,filename):
        continue
    
    if not opt_excl == "":
      if re.search(opt_excl,filename):
        continue
    
    if opt_list == 1:
      ftp.sendcmd("TYPE i")
      print "[+] Filename: "+str(filename)+" size: "+str(int(ftp.size(str(filename)))/1024)+" kB"
      continue

    if not os.path.exists(casedir):
      os.makedirs(casedir)

    global ftpatt 
    ftpatt = str(filename)
    try:
      filelist[ftpatt] += 1
    except KeyError:
      filelist[ftpatt] = 0

    if filelist[ftpatt] > 0:
      name = re.search("^(.+)(\.\S{1,4})$",ftpatt)
      if name:
        temp = name.group(1)+"_"+str(filelist[ftpatt])+name.group(2)
        ftpatt = temp
      else:
        temp = ftpatt + "_"+str(filelist[ftpatt])
        ftpatt = temp

    exists = 0
    
    # do we overwrite or not?
    if opt_over == 0:
      try:
        save = open(casedir+ftpatt,"r")
        save.close()
        exists = 1
      except IOError:
        pass
   
    if exists == 0:
      print "[+] Downloading "+str(ftpatt)+"\r",
      try:
        global ftpfile, fcount, fsize, ftpprogind 
        ftpfile = open(casedir+ftpatt,"wb")
        fcount = 0
        ftp.sendcmd("TYPE i")
        fsize = ftp.size(str(filename))
        ftpprogind = "|"
        ftp.retrbinary("RETR "+str(filename),ftpcallback,blocksize=16192)
        ftpfile.close() 
      except:
        os.unlink(casedir+ftpatt)
        print "[!] error while downloading file: "+str(ftpatt)
        continue

      print "[+] Download of "+str(ftpatt)+" size: "+str(fcount/1024)+" kB done"
    else:
      print "[+] File already exists: "+str(ftpatt)

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

  if os.name == "posix":
    conffile = str(os.environ['HOME'])+os.sep+'.cm.conf'
  urlcm = "https://tools.online.juniper.net/cm/"
  ftpserver = ""

  global caseid,opt_incl,opt_excl,opt_list,opt_temp
  global opt_over,opt_user,opt_pass,opt_ucwd,opt_dir

  caseid = ""
  opt_incl = ""
  opt_excl = ""
  opt_list = 0
  opt_temp = 0
  opt_dir = os.curdir 
  opt_over = 0
  opt_user = ""
  opt_pass = ""
  opt_ucwd = 0

  try:
    LoadConf(conffile)
    
    try:
      opt_user = confvar['cmuser']
    except KeyError:
      pass
    
    try:
      opt_pass = confvar['cmpass']
    except KeyError:
      pass

    try:
      opt_dir = confvar['cmdir']
    except KeyError:
      pass

    # options parsing 
    i = 1
    imax = len(sys.argv)
    while 1:
      if i >= imax:
        break
      arg = sys.argv[i]
      if arg == "-t":
        opt_temp = 1
      elif arg == "-l":
        opt_list = 1
      elif arg == "-o":
        opt_over = 1
      elif arg == "-i":
        i += 1
        if i >= imax:
          usage()
        opt_incl = sys.argv[i]
      elif arg == "-e":
        i += 1
        if i >= imax:
          usage()
        opt_excl = sys.argv[i]
      elif arg == "-h":
        usage()
      elif arg == "-d":
        i += 1
        if i >= imax:
          usage()
        opt_dir = sys.argv[i]
      elif arg == "-u":
        i += 1
        if i >= imax:
          usage()
        opt_user = sys.argv[i]
      elif arg == "-p":
        i += 1
        if i >= imax:
          usage()
        opt_pass = sys.argv[i]
      else:
        if re.match("^\d{4}-\d{4}-\d{4}$",arg):
          caseid = arg
        else:
          usage()
      i += 1

    if caseid == "":
      if re.match("^\d{4}-\d{4}-\d{4}$",os.path.basename(os.getcwd())):
        caseid = os.path.basename(os.getcwd())
        opt_dir = ""
        opt_ucwd = 1

    # just to check we have enough information to go further
    if caseid == "" or opt_user == "" or opt_pass == "":
      print "[!] error: either case id or user name or password was not defined"
      usage()

    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    try:
      dat = urllib2.urlopen(urlcm)
    except urllib2.URLError as errstr:
      print "[!] problem with connecting to the CM, ERROR:"+str(errstr)
      sys.exit(1)
    
    sleep(0.5)

    print "[+] logging into the cm\r",
    try:
      fparser = LoginForm()
      fparser.parse(dat.read())
      form = fparser.get_form()
      form['USER'] = opt_user
      form['PASSWORD'] = opt_pass
      dat = urllib2.urlopen(dat.geturl(),urlencode(form))
    except urllib2.URLError as errstr:
      print "[!] error while logging into cm, ERROR:"+str(errstr)
      sys.exit(1)

    sleep(0.25)
    
    print "[+] searching for "+str(caseid)+"\r",
    try:
      fparser = CaseForm()
      fparser.parse(dat.read())
      form = fparser.get_form()
      form['keyword'] = caseid
      form['fr'] = "5"
      dat = urllib2.urlopen(urlcm+"case_results.jsp",urlencode(form))
    except urllib2.URLError as errstr:
      print "[!] error while searching for the case "+str(caseid)+", ERROR:"+str(errstr)
      sys.exit(1)

    sleep(0.25)

    print "[+] "+str(caseid)+": getting details\r",
    try:
      text = dat.read()
      cid = re.search("href=\"javascript:setCid\(\'(.+?)\'",text)
      fparser = CaseDetailsForm()
      fparser.parse(text)
      form = fparser.get_form()
      form['cid'] = cid.group(1)
      dat = urllib2.urlopen(urlcm+"case_detail.jsp",urlencode(form))
    except AttributeError as errstr:
      print "[!] error while trying to get case "+str(caseid)+" details, ERROR:"+str(errstr)
      sys.exit(1)
    except urllib2.URLError as errstr:
      print "[!] error while trying to get case "+str(caseid)+" details, ERROR:"+str(errstr) 
      sys.exit(1)

    sleep(0.25)

    print "[+] "+str(caseid)+": searching for files\r",
    try:
      fparser = CaseAttachForm()
      fparser.parse(dat.read())
      form = fparser.get_form()
      dat = urllib2.urlopen(urlcm+"case_attachments.jsp",urlencode(form))
    except urllib2.URLError:
      print "[!] error while searching for case "+str(caseid)+" attachments."
      sys.exit(1)

    sleep(0.25)
    text = dat.read()
    attach = re.findall("href=\"(AttachDown/.+?)\"",text)
    attssize = re.findall("<td class=\"tbc\" width=\"\d+%\">\s*(\d+)\s*<\/td>",text)
    attssize.reverse()

    opt_dir = opt_dir.rstrip(os.sep)
    casedir = str(opt_dir)+os.sep+str(caseid)+os.sep
    if opt_temp == 1:
      casedir = str(opt_dir)+os.sep+"temp"+os.sep+str(caseid)+os.sep

    if opt_ucwd == 1:
      casedir = os.curdir+os.sep 

    if opt_list == 0:
      print "[+] "+str(caseid)+": will download to "+str(casedir)

    print "[+] "+str(caseid)+": found total of "+str(len(attach))+" attachment(s)"

    filelist = dict()

    # looping through the attachments
    for att in attach:
      filename = re.search("AttachDown/(.+?)\?OBJID=(.+?)\&",att)
      try:
        attsize = int(attssize.pop())
      except IndexError:
        attsize = "?"

      # just listing attachments
      if opt_list == 1:
        
        if not opt_incl == "":
          if not re.search(opt_incl,filename.group(1)):
            continue
         
        if not opt_excl == "":
          if re.search(opt_excl,filename.group(1)):
            continue

        print "[+] ObjID: "+str(unquote(filename.group(2)))+"  Filename: "+str(filename.group(1))+"  Size: "+str(attsize)+" KB"
      else:

        # downloading attachments
        if not opt_incl == "":
          if not re.search(opt_incl,filename.group(1)):
            continue
        
        if not opt_excl == "":
          if re.search(opt_excl,filename.group(1)):
            continue
        
        if not os.path.exists(casedir):
          os.makedirs(casedir)

        caseatt = str(filename.group(1))
        try:
          filelist[caseatt] += 1
        except KeyError:
          filelist[caseatt] = 0

        if filelist[caseatt] > 0:
          name = re.search("^(.+)(\.\S{1,4})$",caseatt)
          if name:
            temp = name.group(1)+"_"+str(filelist[caseatt])+name.group(2)
            caseatt = temp
          else:
            temp = caseatt + "_"+str(filelist[caseatt])
            caseatt = temp

        exists = 0
        
        # do we overwrite or not?
        if opt_over == 0:
          try:
            save = open(casedir+caseatt,"r")
            save.close()
            exists = 1
          except IOError:
            pass

        if exists == 0:
          try:
            att = urllib2.urlopen(urlcm+quote(att))
          except urllib2.HTTPError as errstr:
            print "[!] HTTP error while downloading "+str(caseatt)+" ERROR:"+str(errstr).replace(os.linesep," ")
            continue

          csize = 0
          try:
            save = open(casedir+caseatt,"w")
            progind = "|"
            while 1:
              data = att.read(16192)
              csize = csize + len(data)
              progind = progressindicator(progind)
              if attsize == "?":
                print "["+str(progind)+"] Getting "+str(caseatt)+" : "+str(csize/1024)+" kB\r",
              else:
                print "["+str(progind)+"] Getting "+str(caseatt)+" : "+str(csize/1024)+" kB ("+str(int((float(csize)/(attsize*1000))*100))+"%)\r",
              if not data:
                break
              save.write(data)
            save.close()
            print "[+] Download of "+str(caseatt)+" size: "+str(csize/1024)+" kB done"
          except IOError as errstr:
            os.unlink(casedir+caseatt)
            print "[!] error while downloading file: "+str(caseatt)+" ERROR:"+str(errstr)
        else:
          print "[+] File already exists: "+str(caseatt)
   
    ### FTP SERVER
    print "[+] Checking ftp server \r",
    ftp = FTP('svl-jtac-tool02.juniper.net')
    ftp.login(opt_user,opt_pass)
    try:
      ftp.cwd("/volume/ftp/pub/incoming/"+caseid)
      ftpcheck(caseid,casedir,ftp)
    except error_perm:
      pass
    
    ### checking sftp folder
    try:
      ftp.cwd("/volume/sftp/pub/incoming/"+caseid)
      ftpcheck(caseid,casedir,ftp)
    except error_perm:
      pass

    ftp.quit()
        
  except KeyboardInterrupt:
    print "[!] program interrupted, exiting"
    sys.exit(1)
