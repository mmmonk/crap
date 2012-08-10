#!/usr/bin/env python

# $Id: 20120811$
# $Date: 2012-08-11 01:24:14$
# $Author: Marek Lukaszuk$

import os
import re
import sys
import time
import urllib2
from sgmllib import SGMLParser
from urllib import urlencode,unquote,quote
from cookielib import CookieJar
from ftplib import FTP,error_perm
from getpass import getpass

### TODO:
# - add check for unicode,
# - add check if the filename is not anything funny, like for example "~/.ssh/config"
# - and in general try to verify all the data from the server

version = "20120808"

# class for unbuffering stdout
class Unbuffered:
  def __init__(self, stream):
    self.stream = stream
  def write(self, data):
    self.stream.write(data)
    self.stream.flush()
  def __getattr__(self, attr):
    return getattr(self.stream, attr)

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
-nd           don't create the case directory just dump eveything into root of the specified directory,\n\
-i regexp     (include) download or list only attachments which filenames match regexp,\n\
-e regexp     (exclude) skip attachments which filenames match regexp,\n\
-h            this help,\n\
-n value      number of newest attachments to download/list from CM, this will skip FTP and SFTP,\n\
-l            just list case attachments without downloading,\n\
-o            force overwrite of the files,\n\
-p pass       password used for the CM,\n\
-fp pass      password used for ftp (if not set this will be the same as -p),\n\
              if value of this will be \"0\" then you will be asked for the password,\n\
-s            show case status, customer information and exit, don't download anything,\n\
-t            this will download attachments to a folder \"temp\"\n\
              in the destination folder (for cases that you just want to look at),\n\
-u user       user name used for the CM,\n\
-dc           disable colors,\n\
-bbg          bright background (different color theme),\n\
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
    try:
      conft = line.replace(os.linesep,'').split("=")
      confvar[conft[0]] = conft[1]
    except:
      pass
    line = conf.readline()

def progressindicator(sign):
  '''
  rotating line, progress indicator
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

def ts2time(ts,withseconds=0):
  ts = int(ts)

  if ts < 60:
    return str(ts)+"s"
  elif ts < 3600:
    if withseconds == 1:
      return str(ts/60)+"m "+str(ts%60)+"s"
    else:
      return str(ts/60)+"m"
  else:
    if withseconds == 1:
      return str(ts/3600)+"h "+str((ts%3600)/60)+"m "+str((ts%3600)%60)+"s"
    else:
      return str(ts/3600)+"h "+str((ts%3600)/60)+"m"

def ftpcallback(data):
  '''
  call back function used while getting data via ftplib
  '''
  global fcount, ftpfile, ftpprogind
  fcount+=len(data)
  ftpfile.write(data)
  ftpprogind = progressindicator(ftpprogind)
  done = (float(fcount)/fsize)*100
  if done == 0:
    eta = "?"
  else:
    eta = ts2time(int(((time.time()-ftpstime)/done)*(100-done)))
  print ct.style(ct.ok,"["+str(ftpprogind)+"]")+ct.style(ct.text," Getting ")+ct.style(ct.att,str(ftpatt))+" "+ct.style(ct.num,str(fcount/1024))+ct.style(ct.text," kB (")+ct.style(ct.num,str(int(done)))+ct.style(ct.text,"% ETA:"+str(eta)+")")+"        \r",

def ftpcheck(filelist,caseid,casedir,ftp):
  '''
  this checks for files inside the specific folder
  of the ftp server, it also makes sure not to overwrite files
  '''
  ftplist = ftp.nlst()
  print ct.style(ct.ok,"[+] ")+ct.style(ct.case,str(caseid))+ct.style(ct.text,": found ")+ct.style(ct.num,str(len(ftplist)))+ct.style(ct.text," file(s) in ")+ct.style(ct.fold,str(ftp.pwd()))
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
      print ct.style(ct.ok,"[+]")+ct.style(ct.text," Filename: ")+ct.style(ct.att,str(filename))+ct.style(ct.text," size: ")+ct.style(ct.num,str(int(ftp.size(str(filename)))/1024))+ct.style(ct.text," kB")
      continue

    if not os.path.exists(casedir):
      os.makedirs(casedir)

    global ftpatt
    ftpatt = str(filename)

    try:
      atttime = time.mktime(time.strptime((str(ftp.sendcmd("MDTM "+filename)).split())[1],"%Y%m%d%H%M%S"))
    except:
      atttime = time.time()

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
        save = open(casedir+os.sep+ftpatt,"r")
        save.close()
        exists = 1
      except IOError:
        pass

    if exists == 0:
      notdir = 1
      try:
        ftp.cwd(filename)
        ftpcheck(filelist,caseid,casedir+os.sep+filename,ftp)
        ftp.cwd("..")
        notdir = 0
      except error_perm:
        pass

      if notdir == 1:
        print ct.style(ct.ok,"[+]")+ct.style(ct.text," Downloading ")+ct.style(ct.att,str(ftpatt))+"\r",
        try:
          global ftpfile, fcount, fsize, ftpprogind, ftpstime
          ftpfile = open(casedir+os.sep+ftpatt,"wb")
          fcount = 0
          ftp.sendcmd("TYPE i")
          fsize = ftp.size(str(filename))
          ftpprogind = "|"
          ftpstime = time.time()
          ftp.retrbinary("RETR "+str(filename),ftpcallback,blocksize=32768)
          ftpfile.close()
        except:
          os.unlink(casedir+os.sep+ftpatt)
          print "[!] error while downloading file: "+ct.style(ct.att,str(ftpatt))
          continue

        print ct.style(ct.ok,"[+]")+ct.style(ct.text," Download of ")+ct.style(ct.att,str(ftpatt))+ct.style(ct.text," size: ")+ct.style(ct.num,str(fcount/1024))+ct.style(ct.text," kB done in "+str(ts2time(int(time.time()-ftpstime),1)))
        os.utime(casedir+os.sep+ftpatt,(atttime,atttime))
        if os.name == "posix":
          os.chmod(casedir+os.sep+ftpatt,0644)
    else:
      print ct.style(ct.ok,"[+]")+ct.style(ct.text," File already exists: ")+ct.style(ct.att,str(ftpatt))

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


class Color:
  normal = "\033[0m"
  black = "\033[30m"
  red = "\033[31m"
  green = "\033[32m"
  yellow = "\033[33m"
  blue = "\033[34m"
  purple = "\033[35m"
  cyan = "\033[36m"
  grey = "\033[37m"

  bold = "\033[1m"
  uline = "\033[4m"
  blink = "\033[5m"
  invert = "\033[7m"

class default_theme:
  
  def style(self,style,text):
    return str(style)+str(text)+str(self.norm)

  att  = ""
  case = ""
  done = ""
  err  = ""
  norm = ""
  ok   = ""
  row1 = ""
  row2 = ""
  text = ""
  fold = ""
  num  = ""

class nocolor_theme(default_theme):
  pass

class color_theme(default_theme):
  ok   = Color.blue+Color.bold
  err  = Color.red
  norm = Color.normal
  text = Color.green
  case = Color.purple
  row1 = Color.cyan+Color.bold
  row2 = Color.cyan
  att  = Color.purple
  fold = Color.grey
  num  = Color.yellow+Color.bold

class bbg_theme(default_theme):
  pass

if __name__ == '__main__':

  sys.stdout = Unbuffered(sys.stdout)

  if os.name == "posix":
    conffile = str(os.environ['HOME'])+os.sep+'.cm.conf'
  urlcm = "https://tools.online.juniper.net/cm/"
  ftpserver = "svl-jtac-tool02.juniper.net"

  global caseid,opt_incl,opt_excl,opt_list,opt_temp
  global opt_over,opt_user,opt_pass,opt_ucwd,opt_dir

  cases = []
  opt_dir = os.curdir
  opt_excl = ""
  opt_fpass = ""
  opt_incl = ""
  opt_list = 0
  opt_news = 0
  opt_nmkd = 0
  opt_over = 0
  opt_pass = ""
  opt_stat = 0
  opt_temp = 0
  opt_ucwd = 0
  opt_user = ""

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

    ct = color_theme()
    
    # options parsing
    i = 1
    imax = len(sys.argv)
    try:
      while 1:
        if i >= imax:
          break
        arg = sys.argv[i]
        if arg == "-t": # temporary folder usage
          opt_temp = 1
        elif arg == "-l": # just list the attachments
          opt_list = 1
        elif arg == "-o": # overwrite the files
          opt_over = 1
        elif arg == "-s": # print the case data
          opt_stat = 1
        elif arg == "-dc": # color support disabled
          ct = nocolor_theme() 
        elif arg == "-bbg": # brigh background theme
          ct = bbg_theme()
        elif arg == "-nd": # don't create the case dir
          opt_nmkd = 1
        elif arg == "-i": # include only files matching regex
          i += 1
          if i >= imax:
            usage()
          opt_incl = sys.argv[i]
        elif arg == "-e": # exclude only files matching regex
          i += 1
          if i >= imax:
            sys.exit(1)
          opt_excl = sys.argv[i]
        elif arg == "-h": # print usage/help
          sys.exit(1)
        elif arg == "-d": # write files to this directory
          i += 1
          if i >= imax:
            sys.exit(1)
          opt_dir = sys.argv[i]
        elif arg == "-u": # username for the case system
          i += 1
          if i >= imax:
            sys.exit(1)
          opt_user = sys.argv[i]
        elif arg == "-n": # download only n latest attachemnts
          i += 1
          if i >= imax:
            sys.exit(1)
          opt_news = int(sys.argv[i])
        elif arg == "-p": # password for the case system
          i += 1
          if i >= imax:
            sys.exit(1)
          opt_pass = sys.argv[i]
        elif arg == "-fp": # ftp password
          i += 1
          if i >= imax:
            sys.exit(1)
          opt_fpass = sys.argv[i]
        else:
          if re.match("^\d{4}-\d{4}-\d{4}$",arg):
            cases.append(arg)
          else:
            sys.exit(1)
        i += 1
    except:
      usage()


    if len(cases) == 0:
      m = re.match("^\d{4}-\d{4}-\d{4}",os.path.basename(os.getcwd()))
      if m != None:
        cases.append(m.group(0))
        opt_dir = ""
        opt_ucwd = 1

    # just to check we have enough information to go further
    if len(cases) == 0 or opt_user == "":
      print ct.style(ct.err,"[!] error: either case id or user name was not defined")
      usage()

    # normal password
    if opt_pass == "":
      try:
        opt_pass = getpass("Please enter password: ").strip()
      except:
        usage()

    if opt_pass == "":
      print "[!] error: password can not be empty"
      usage()

    # ftp password
    if opt_fpass == "0":
      try:
        opt_fpass = getpass("Please enter FTP password: ").strip()
      except:
        usage()

    if opt_fpass == "":
      opt_fpass = opt_pass

    # here we start the actual connection 
    cj = CookieJar()
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
    urllib2.install_opener(opener)
    try:
      dat = urllib2.urlopen(urlcm)
    except urllib2.URLError as errstr:
      print ct.style(ct.err,"[!] problem with connecting to the CM,\nERROR:"+str(errstr))
      sys.exit(1)

    print ct.style(ct.ok,"[+]")+ct.style(ct.text," logging into the CM")+"\r",
    try:
      fparser = LoginForm()
      fparser.parse(dat.read())
      form = fparser.get_form()
      form['USER'] = opt_user
      form['PASSWORD'] = opt_pass
      dat = urllib2.urlopen(dat.geturl(),urlencode(form))
    except urllib2.URLError as errstr:
      print ct.style(ct.err,"[!] error while logging into CM,\nERROR:"+str(errstr))
      sys.exit(1)

    mainpage = dat.read()

    if opt_news == 0 and opt_stat == 0:
      print ct.style(ct.ok,"[+]")+ct.style(ct.text," logging into ftp server")+"\r",
      # trying to login to the ftp server
      try:
        ftp = FTP(ftpserver)
        ftp.login(opt_user,opt_fpass)
      except:
        print ct.style(ct.err,"[!] error while connecting to the ftp server "+str(ftpserver))
        sys.exit(1)

    # the main loop over the case IDs
    for caseid in cases:

      print ct.style(ct.ok,"[+]")+" "+ct.style(ct.case,str(caseid))+ct.style(ct.text,": searching")+"\r",
      try:
        fparser = CaseForm()
        fparser.parse(mainpage)
        form = fparser.get_form()
        form['keyword'] = caseid
        form['fr'] = "5"
        dat = urllib2.urlopen(urlcm+"case_results.jsp",urlencode(form))
      except urllib2.URLError as errstr:
        print ct.style(ct.err,"[!] error while searching for the case ")+ct.style(ct.case,str(caseid))+",\n"+ct.style(ct.err,"ERROR:"+str(errstr))
        sys.exit(1)

      print ct.style(ct.ok,"[+] ")+ct.style(ct.case,str(caseid))+ct.style(ct.text,": getting details")+"\r",
      try:
        text = dat.read()
        cid = re.search("href=\"javascript:setCid\(\'(.+?)\'",text)
        fparser = CaseDetailsForm()
        fparser.parse(text)
        form = fparser.get_form()
        form['cid'] = cid.group(1)
        dat = urllib2.urlopen(urlcm+"case_detail.jsp",urlencode(form))
      except AttributeError as errstr:
        print ct.style(ct.err,"[!] error while trying to get case ")+ct.style(ct.case,str(caseid))+ct.style(ct.err," details. >>> Probably your password and/or username are incorrect <<< .\nERROR:"+str(errstr))
        sys.exit(1)
      except urllib2.URLError as errstr:
        print ct.style(ct.err,"[!] error while trying to get case ")+ct.style(ct.case,str(caseid))+ct.style(ct.err," details,\nERROR:"+str(errstr))
        sys.exit(1)

      # this is for printing the detail status of the case
      if opt_stat == 1:
        text = re.sub("\s+"," ",dat.read().replace("\n","").replace("\r",""))
        contact = re.findall("onclick=\"NewWindow\('(my_contact_info\.jsp\?contact=.+?')",text)
        
        line = 0 
        if len(contact) > 0:
          dat = urllib2.urlopen(urlcm+contact[0])
          contact = re.sub("\s+"," ",dat.read().replace("\n","").replace("\r",""))
          contact = re.sub("</?a(>| href=.+?>)","",contact)
          for desc,value in re.findall("<td class=\"tbcbold\">(.+?):</td>.*?<td class=\"tbc\">(.+?)</td>",contact):
            if line % 2 == 0:
              rowcol = ct.row1
            else:
              rowcol = ct.row2
            print "["+ct.style(ct.case,str(caseid))+"]"+ct.style(rowcol," Contact details - "+str(desc)+": "+str(value).replace("&nbsp;","").strip())
            line += 1
        
        for desc,value in re.findall("<b>((?:\w|\s)+?):&nbsp;&nbsp;<\/b>(.+?)<",text,re.I):
          if not desc in ["Current Status","Problem Description"]:
            if line % 2 == 0:
              rowcol = ct.row1
            else:
              rowcol = ct.row2
            print "["+ct.style(ct.case,str(caseid))+"] "+ct.style(rowcol,str(desc)+": "+str(value).replace("&nbsp;","").strip())
            line += 1
        continue # we drop out of the loop here

      print ct.style(ct.ok,"[+] ")+ct.style(ct.case,str(caseid))+ct.style(ct.text,": searching for files")+"\r",
      try:
        fparser = CaseAttachForm()
        fparser.parse(dat.read())
        form = fparser.get_form()
        dat = urllib2.urlopen(urlcm+"case_attachments.jsp",urlencode(form))
      except urllib2.URLError:
        print "[!] error while searching for case "+ct.style(ct.case,str(caseid))+" attachments."
        sys.exit(1)

      text = dat.read()
      attach = re.findall("href=\"(AttachDown/.+?)\"",text)
      attssize = re.findall("<td class=\"tbc\" width=\"\d+%\">\s*(\d+)\s*<\/td>",text)
      attssize.reverse()
      attmtime = re.findall("<td class=\"tbc\" width=\"\d+%\">\s*(\d+-\d+-\d+ \d+:\d+:\d+)\.0\s*<\/td>",text)
      attmtime.reverse()

      opt_dir = opt_dir.rstrip(os.sep)
      casedir = str(opt_dir)+os.sep+str(caseid)+os.sep
      if opt_temp == 1:
        casedir = str(opt_dir)+os.sep+"temp"+os.sep+str(caseid)+os.sep

      if opt_ucwd == 1:
        casedir = os.curdir+os.sep

      if opt_nmkd == 1:
        casedir = str(opt_dir)+os.sep

      casedir = os.path.normpath(casedir)
      if opt_list == 0:
        print ct.style(ct.ok,"[+] ")+ct.style(ct.case,str(caseid))+ct.style(ct.text,": will download to ")+ct.style(ct.fold,str(casedir)+"         ")

      maxcmatt = len(attach)
      print ct.style(ct.ok,"[+] ")+ct.style(ct.case,str(caseid))+ct.style(ct.text,": found total of ")+ct.style(ct.num,str(maxcmatt))+ct.style(ct.text," attachment(s)")

      filelist = dict()

      curcmatt = 1
      # looping through the attachments
      for att in attach:
        filename = re.search("AttachDown/(.+?)\?OBJID=(.+?)\&",att)
        try:
          attsize = int(attssize.pop())
        except IndexError:
          attsize = "?"

        try:
          # attachemnts upload time is in PST/PDT we need to convert it to local time
          os.environ['TZ'] = "America/Los_Angeles"
          time.tzset()
          atttime = int(time.mktime(time.strptime(attmtime.pop(),"%Y-%m-%d %H:%M:%S")))
          os.environ.pop('TZ')
          time.tzset()

        except:
          atttime = int(time.time())

        # just listing attachments
        if opt_list == 1:

          # filtering - include
          if not opt_incl == "":
            if not re.search(opt_incl,filename.group(1)):
              continue

          #filtering - exclude
          if not opt_excl == "":
            if re.search(opt_excl,filename.group(1)):
              continue

          # download N newest attachements
          if opt_news > 0:
            if curcmatt <= maxcmatt - opt_news:
              curcmatt += 1
              continue

          print ct.style(ct.ok,"[+]")+ct.style(ct.text," ObjID: "+str(unquote(filename.group(2)))+"  Filename: ")+ct.style(ct.att,str(filename.group(1)))+ct.style(ct.text," size: ")+ct.style(ct.num,str(attsize))+ct.style(ct.text," KB")
        else:

          # downloading attachments
          # filtering - include
          if not opt_incl == "":
            if not re.search(opt_incl,filename.group(1)):
              continue

          # filtering - exclude
          if not opt_excl == "":
            if re.search(opt_excl,filename.group(1)):
              continue

          # download N newest attachments
          if opt_news > 0:
            if curcmatt <= maxcmatt - opt_news:
              curcmatt += 1
              continue

          # lets make sure that we have the destination directory
          if not os.path.exists(casedir):
            os.makedirs(casedir)
            if os.name == "posix":
              os.chmod(casedir,0755)

          # and that the names don't repeat
          caseatt = str(filename.group(1))
          try:
            filelist[caseatt] += 1
          except KeyError:
            filelist[caseatt] = 0

          # if the name repeats modify the name
          if filelist[caseatt] > 0:
            name = re.search("^(.+)(\.\S{1,4})$",caseatt)
            if name: # if we have extension, then add a number before ext
              temp = name.group(1)+"_"+str(filelist[caseatt])+name.group(2)
              caseatt = temp
            else: # if we don't see any extension then add the number at the end
              temp = caseatt + "_"+str(filelist[caseatt])
              caseatt = temp

          exists = 0

          # do we overwrite or not?
          if opt_over == 0:
            try:
              save = open(casedir+os.sep+caseatt,"r")
              save.close()
              exists = 1
            except IOError:
              pass

          if exists == 0:
            try:
              att = quote(att)
              # this is to encode dot ".", otherwise we get HTTP error 500
              att = re.sub("\.","%46",att)
              att = urllib2.urlopen(urlcm+att)
            except urllib2.HTTPError as errstr:
              if "302" in str(errstr):
                print ct.style(ct.ok,"[+] ")+ct.style(ct.att,str(caseatt))+ct.style(ct.text," - this is probably from SFTP, will try to get it later")
              else:
                print "[!] HTTP error while downloading "+str(caseatt)+" ERROR:"+str(errstr).replace(os.linesep," ")
              continue

            csize = 0
            try:
              save = open(casedir+os.sep+caseatt,"w")
              progind = "|"
              stime = time.time()
              while 1:
                data = att.read(32768)
                csize = csize + len(data)
                progind = progressindicator(progind)
                if attsize == "?":
                  print "["+str(progind)+"] Getting "+ct.style(ct.att,str(caseatt))+" : "+str(csize/1024)+" kB\r",
                else:
                  done = (float(csize)/(attsize*1000))*100
                  if done == 0:
                    eta = "?"
                  else:
                    eta = ts2time(int(((time.time()-stime)/done)*(100-done)))
                  print ct.style(ct.ok,"["+str(progind)+"]")+ct.style(ct.text," Getting ")+ct.style(ct.att,str(caseatt))+ct.style(ct.text," : ")+ct.style(ct.num,str(csize/1024))+ct.style(ct.text," kB (")+ct.style(ct.num,str(int(done)))+ct.style(ct.text,"% ETA:"+str(eta)+")")+"        \r",
                if not data:
                  break
                save.write(data)
              save.close()
              print ct.style(ct.ok,"[+]")+ct.style(ct.text," Download of ")+ct.style(ct.att,str(caseatt))+ct.style(ct.text," size: ")+ct.style(ct.num,str(csize/1024))+ct.style(ct.text," kB done in "+str(ts2time(int(time.time()-stime),1)))
              os.utime(casedir+os.sep+caseatt,(atttime,atttime))
              if os.name == "posix":
                os.chmod(casedir+os.sep+caseatt,0644)
            except IOError as errstr:
              os.unlink(casedir+caseatt)
              print "[!] error while downloading file: "+ct.style(ct.att,str(caseatt))+" ERROR:"+str(errstr)
          else:
            print ct.style(ct.ok,"[+]")+ct.style(ct.text," File already exists: ")+ct.style(ct.att,str(caseatt))

      ### FTP SERVER
      if opt_news == 0:

        ### checking ftp upload directory
        try:
          ftp.cwd("/volume/ftp/pub/incoming/"+caseid)
          ftpcheck(filelist,caseid,casedir,ftp)
        except error_perm:
          pass

        ### checking sftp upload directory
        try:
          ftp.cwd("/volume/sftp/pub/incoming/"+caseid)
          ftpcheck(filelist,caseid,casedir,ftp)
        except error_perm:
          pass

    if opt_news == 0 and opt_stat == 0:
      ftp.quit()

  except KeyboardInterrupt:
    print "[!] program interrupted, exiting"
    sys.exit(1)

