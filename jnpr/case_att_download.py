#!/usr/bin/env python

# $Id: 20120926$
# $Date: 2012-09-26 23:22:00$
# $Author: Marek Lukaszuk$

from sgmllib import SGMLParser
from urllib import urlencode,unquote,quote
from cookielib import LWPCookieJar
from ftplib import FTP,error_perm,error_temp
from getpass import getpass
import os, re, sys, time, socket, urllib2

# the default timeout for all operations
socket.setdefaulttimeout(60.0)

version = "20120910"

# TODO - make the HTTP connection use keep-alive
#>>> import httplib
#>>> a = httplib.HTTPConnection("wp.pl",80)
#>>> a.connect()

# class for unbuffering stdout
class Unbuffered:
  def __init__(self, stream):
    self.stream = stream
  def write(self, data):
    self.stream.write(data)
    self.stream.flush()
  def __getattr__(self, attr):
    return getattr(self.stream, attr)

class ftpcallback:
  '''
  class for the ftp callback
  '''
  def __init__(self, ftpatt, ftpfile, fsize, ftpstime):
    self.fcount = 0
    self.fsize = fsize
    self.ftpatt = ftpatt
    self.ftpfile = ftpfile
    self.ftpprogind = "|"
    self.ftpstime = ftpstime
    self.lastprint = int(time.time())

  def main(self, data):
    '''
    call back function used while getting data via ftplib
    '''
    self.fcount += len(data)
    self.ftpfile.write(data)

    if self.lastprint < int(time.time()) and sys.stdout.isatty():

      self.lastprint = int(time.time())

      done = (float(self.fcount)/self.fsize)*100

      if done == 0:
        eta = "?"
      else:
        eta = ts2time(int(((time.time()-self.ftpstime)/done)*(100-done)))

      self.ftpprogind = progressindicator(self.ftpprogind)
      txt.ok(ct.style(ct.ok,"["+str(self.ftpprogind)+"]")+ct.style(ct.text," Getting ")+ct.style(ct.att,str(self.ftpatt))+" "+ct.style(ct.num,str(self.fcount/1024))+ct.style(ct.text," kB (")+ct.style(ct.num,str(int(done)))+ct.style(ct.text,"% ETA:"+str(eta)+")")+"        \r",1)

class FormParser(SGMLParser):
  '''
  This is a generic form parser
  '''
  this_form = ""

  def __init__(self, verbose = 0):
    SGMLParser.__init__(self, verbose)
    self.form = {}
    self.inside_form = 0

  def do_input(self, attributes):
    if self.inside_form == 1 and 'hidden' in attributes[0]:
        self.form[attributes[1][1]] = attributes[2][1]

  def end_form(self):
    self.inside_form = 0

  def get_form(self,s,f):
    self.reset()
    self.this_form = f
    self.feed(s)
    self.close()
    return self.form

  def start_form(self, attributes):
    for name, value in attributes:
      if name == "name" and value == self.this_form:
        self.inside_form = 1
        break

class FormUpload(FormParser):

  def do_input(self, attributes):
    if self.inside_form == 1:
        self.form[attributes[1][1]] = attributes[2][1]

  def start_form(self, attributes):
    for name, value in attributes:
      if name == "action" and value == self.this_form:
        self.inside_form = 1
        break

class Color:
  '''
  ASCII codes
  '''
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
  '''
  parent class for the themes
  '''
  def style(self,style,text):
    return str(style)+str(text)+str(self.norm)

  att  = "" # filename color
  case = "" # case id color
  err  = "" # error color
  fold = "" # folder/directory color
  norm = "" # normal/default settings
  num  = "" # numbers
  ok   = "" # [+] color
  row1 = "" # first color for case details display
  row2 = "" # second color for case details display
  text = "" # normal text color
  warn = "" # warning message

class nocolor_theme(default_theme):
  '''
  color theme for disable colors option
  '''
  pass

class color_theme(default_theme):
  '''
  default color theme
  '''
  att  = Color.purple+Color.bold
  case = Color.purple
  err  = Color.red+Color.bold
  fold = Color.grey
  norm = Color.normal
  num  = Color.yellow+Color.bold
  ok   = Color.green
  row1 = Color.cyan+Color.bold
  row2 = Color.cyan
#  text = Color.green+Color.bold
  warn = Color.yellow+Color.bold

class bbg_theme(default_theme):
  '''
  bright background color theme
  '''
  pass

class msg:
  '''
  messages printing class
  '''
  caseid = ""

  def case(self,cid):
    '''
    sets case id
    '''
    self.caseid = cid

  def printcase(self,sign):
    if self.caseid == "":
      return sign
    else:
      return self.caseid

  def ok(self,mesg,force_print=0):
    '''
    normal messages
    '''
    if opt_quiet == 0 or force_print == 1:
      print ct.style(ct.ok,"[")+ct.style(ct.case,str(self.printcase("+")))+ct.style(ct.ok,"] ")+str(mesg),

  def warn(self,mesg):
    '''
    warning messages
    '''
    print ct.style(ct.warn,"["+str(self.printcase("-"))+"] warning: "+str(mesg))

  def err(self,mesg):
    '''
    error messages
    '''
    print ct.style(ct.err,"["+str(self.printcase("!"))+"] error: "+str(mesg))

class cookiemonster (LWPCookieJar):
  '''
  extension of cookie class for reusing cookies between sessions
  '''
  def store(self):
    if not self.filename == "":
      try:
        self.save(self.filename,ignore_discard=True,ignore_expires=True)
        if os.name == "posix":
          os.chmod(self.filename,0600)
      except:
        pass

def usage():
  '''
  function printing usage/help information
  '''
  print "\nUsage: "+str(sys.argv[0])+" <options> Case-IDCa-seID Case-IDCa-seID Case-IDCa-seID\n\
\n\
Author: Marek Lukaszuk\n\
Version: "+str(version)+"\n\n\
Options:\n\
-q            be quiet, print only information when a file is downloaded,\n\
-d directory  directory where to download attachments,\n\
              inside that directory a directory with the case number will be created,\n\
-nd           don't create the case directory just dump everything into root of the specified directory,\n\
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

  return confvar

def fileexists(filename):
  try:
    save = open(filename,"r")
    save.close()
    return 1
  except IOError:
    return 0

def uniqfilename(flist, filename):
  '''
  makes sure that the filenames are unique
  '''
  try:
    flist[filename] += 1
  except KeyError:
    flist[filename] = 0
    return filename

  name = re.search("^(.+)(\.\S{1,4})$",filename)
  if name: # if we have extension, then add a number before ext
    return name.group(1)+"_"+str(flist[filename])+name.group(2)
  else: # if we don't see any extension then add the number at the end
    return filename + "_"+str(flist[filename])

def progressindicator(sign):
  '''
  rotating line, progress indicator
  '''
  if sign == "|":
    return "/"
  elif sign == "/":
    return "-"
  elif sign == "-":
    return "\\"
  else:
    return "|"

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

def ftpcheck(filelist,caseid,lcasedir,ftp,opt_incl,opt_excl,opt_list,opt_over):
  '''
  this checks for files inside the specific folder
  of the ftp server, it also makes sure not to overwrite files
  '''
  try: # this triggers exception if the directory is empty
    ftplist = ftp.nlst()
  except error_perm:
    return

  txt.ok(ct.style(ct.text,"found ")+ct.style(ct.num,str(len(ftplist)))+ct.style(ct.text," file(s) in ")+ct.style(ct.fold,str(ftp.pwd()))+"\n")

  for filename in ftplist:
    filename = filename.replace(os.sep,"_").encode('ascii')

    try: # this checks if we have directories, if we do we go recursive
      ftp.cwd(filename)
      ftpcheck(filelist,caseid,lcasedir+os.sep+filename,ftp,opt_incl,opt_excl,opt_list,opt_over)
      ftp.cwd("..")
      continue
    except error_perm:
      pass

    if not opt_incl == "" and not re.search(opt_incl,filename):
        continue

    if not opt_excl == "" and re.search(opt_excl,filename):
        continue

    if opt_list == 1:
      ftp.sendcmd("TYPE i")
      txt.ok(ct.style(ct.text,"filename: ")+ct.style(ct.att,str(filename))+ct.style(ct.text," size: ")+ct.style(ct.num,str(int(ftp.size(str(filename)))/1024))+ct.style(ct.text," kB")+"\n",1)
      continue

    try:
      atttime = time.mktime(time.strptime((str(ftp.sendcmd("MDTM "+filename)).split())[1],"%Y%m%d%H%M%S"))
    except:
      atttime = time.time()

    ftpatt = uniqfilename(filelist,str(filename))

    # do we overwrite or not?
    if opt_over == 0 and fileexists(lcasedir+os.sep+ftpatt):
      txt.ok(ct.style(ct.text,"file already exists: ")+ct.style(ct.att,str(ftpatt))+"\n")
      continue

    if not os.path.exists(lcasedir):
      os.makedirs(lcasedir,mode=0755)

    txt.ok(ct.style(ct.text,"downloading ")+ct.style(ct.att,str(ftpatt))+"\r",1)
    try:
      ftpfile = open(lcasedir+os.sep+ftpatt,"wb")
      ftp.sendcmd("TYPE i")
      ftpstime = time.time()
      ftpcb = ftpcallback(ftpatt, ftpfile, ftp.size(ftpatt), ftpstime)
      ftp.retrbinary("RETR "+ftpatt,ftpcb.main,blocksize=32768)
      ftpfile.close()
      fcount = ftpcb.fcount
    except:
      os.unlink(lcasedir+os.sep+ftpatt)
      txt.warn("error while downloading file: "+ct.style(ct.att,str(ftpatt)))
      continue

    txt.ok(ct.style(ct.text,"download of ")+ct.style(ct.att,str(ftpatt))+ct.style(ct.text," size: ")+ct.style(ct.num,str(fcount/1024))+ct.style(ct.text," kB done in "+str(ts2time(int(time.time()-ftpstime),1)))+"\n",1)
    os.utime(lcasedir+os.sep+ftpatt,(atttime,atttime))
    if os.name == "posix":
      os.chmod(lcasedir+os.sep+ftpatt,0644)

if __name__ == '__main__':

  sys.stdout = Unbuffered(sys.stdout)

  cookiefile = ""

  if os.name == "posix":
    conffile = str(os.environ['HOME'])+os.sep+'.cm.conf'
    cookiefile = str(os.environ['HOME'])+os.sep+'.cm.cookies'
  urlcm = "https://tools.online.juniper.net/cm/"
  ftpserver = "svl-jtac-tool02.juniper.net"

  cases = dict()
  opt_dir = os.curdir
  opt_excl = ""
  opt_fpass = ""
  opt_incl = ""
  opt_list = 0
  opt_news = 0
  opt_nmkd = 0
  opt_over = 0
  opt_pass = ""
  opt_quiet = 0
  opt_stat = 0
  opt_temp = 0
  opt_ucwd = 0
  opt_user = ""
  opt_attach = 0

  try:
    confvar = LoadConf(conffile)

    try:
      opt_user = confvar['cmuser']
    except:
      pass

    try:
      opt_pass = confvar['cmpass']
    except:
      pass

    try:
      opt_dir = confvar['cmdir']
    except:
      pass

    # by default we use colors
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
        elif arg == "-a": # upload files
          opt_attach = 1
        elif arg == "-l": # just list the attachments
          opt_list = 1
        elif arg == "-o": # overwrite the files
          opt_over = 1
        elif arg == "-s": # print the case data
          opt_stat = 1
        elif arg == "-q": # print only important messages
          opt_quiet = 1
        elif arg == "-dc": # color support disabled
          ct = nocolor_theme()
        elif arg == "-bbg": # bright background theme
          ct = bbg_theme()
        elif arg == "-nd": # don't create the case dir
          opt_nmkd = 1
        elif arg == "-i": # include only files matching regex
          i += 1
          opt_incl = sys.argv[i]
        elif arg == "-e": # exclude only files matching regex
          i += 1
          opt_excl = sys.argv[i]
        elif arg == "-h": # print usage/help
          sys.exit(1)
        elif arg == "-d": # write files to this directory
          i += 1
          opt_dir = sys.argv[i]
        elif arg == "-u": # username for the case system
          i += 1
          opt_user = sys.argv[i]
        elif arg == "-n": # download only n latest attachments
          i += 1
          opt_news = int(sys.argv[i])
        elif arg == "-p": # password for the case system
          i += 1
          opt_pass = sys.argv[i]
        elif arg == "-fp": # ftp password
          i += 1
          opt_fpass = sys.argv[i]
        else:
          if re.match("^\d{4}-\d{4}-\d{4}$",arg):
            cases[arg] = 1
          else:
            sys.exit(1)
        i += 1
    except:
      usage()

    txt = msg()

    if not sys.stdout.isatty():
      ct = nocolor_theme()
      opt_quiet = 1

    if len(cases) == 0:
      m = re.match("^\d{4}-\d{4}-\d{4}",os.path.basename(os.getcwd()))
      if m != None:
        cases[m.group(0)] = 1
        opt_dir = ""
        opt_ucwd = 1

    # just to check we have enough information to go further
    if len(cases) == 0 or opt_user == "":
      txt.err("either case id or user name was not defined")
      sys.exit(1)

    # here we start the actual connection
    cj = cookiemonster(filename=cookiefile)
    try:
      cj.load(ignore_discard=True, ignore_expires=True)
    except IOError:
      pass
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj),urllib2.AbstractHTTPHandler(debuglevel=3))
    opener.addheaders = [('User-agent', 'Mozilla/5.0 (X11; Linux x86_64; rv:16.0) Gecko/20100101 Firefox/16.0'),('Accept-Language','en-us,en;q=0.5'),('Accept','text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'),('Connection','Keep-Alive')]
    urllib2.install_opener(opener)
    try:
      dat = urllib2.urlopen(urlcm)
    except urllib2.URLError as errstr:
      txt.err("problem with connecting to the CM,\nERROR:"+str(errstr))
      sys.exit(1)

    fparser = FormParser()

    text = dat.read()

    if not "Case Management Home" in text:
      # normal password
      if opt_pass == "":
        try:
          opt_pass = getpass("Please enter password: ").strip()
        except:
          usage()

      if opt_pass == "":
        txt.err("password can not be empty")
        sys.exit(1)

    # ftp password
    if opt_fpass == "0":
      try:
        opt_fpass = getpass("Please enter FTP password: ").strip()
      except:
        usage()

    if opt_fpass == "":
      opt_fpass = opt_pass

    if not "Case Management Home" in text:
      txt.ok(ct.style(ct.text,"logging into the CM")+"\r")
      try:
        form = fparser.get_form(text,"Login")
        form['login'] = opt_user
        form['password'] = opt_pass
        dat = urllib2.urlopen(dat.geturl(),urlencode(form))
      except urllib2.URLError as errstr:
        txt.err("can't log into CM,\nERROR:"+str(errstr))
        sys.exit(1)
    else:
      txt.ok(ct.style(ct.text,"in the CM")+"\r")

    mainpage = dat.read()

    if "Login Error" in mainpage:
      txt.err("wrong credentials for CM.")
      sys.exit(1)

    if opt_news == 0 and opt_stat == 0 and opt_attach == 0:
      txt.ok(ct.style(ct.text,"logging into ftp server")+"\r")
      # trying to login to the ftp server
      try:
        ftp = FTP(ftpserver)
        ftp.login(opt_user,opt_fpass)
      except:
        txt.err("can't connect to the ftp server "+str(ftpserver)+": "+str(sys.exc_info()))
        sys.exit(1)

    if "form id=\"Login\" name=\"Login\" method=\"post\"" in mainpage:
      txt.err("something went wrong we are not logged in.")
      sys.exit(1)

    # the main loop over the case IDs
    for caseid in sorted(cases.keys()):

      txt.case(caseid)
      txt.ok(ct.style(ct.text,"case search")+"\r")
      try:
        form = fparser.get_form(mainpage,"Login")
        form['keyword'] = caseid
        form['fr'] = "5"
        dat = urllib2.urlopen(urlcm+"case_results.jsp",urlencode(form))
      except urllib2.URLError as errstr:
        txt.err("while searching for the case\nERROR: "+str(errstr))
        continue

      txt.ok(ct.style(ct.text,"getting details")+"\r")
      try:
        text = dat.read()
        if not caseid in text:
          txt.warn("search returned nothing.")
          continue

        if "Your search did not find any matching results." in text:
          txt.warn("this case id doesn't exists in CM.")
          continue
        cid = re.search("href=\"javascript:setCid\(\'(.+?)\'",text)
        form = fparser.get_form(text,"case_results")
        form['cid'] = cid.group(1)
        dat = urllib2.urlopen(urlcm+"case_detail.jsp",urlencode(form))
      except (AttributeError,urllib2.URLError) as errstr:
        txt.err("while trying to get case details.\nERROR:"+str(errstr))
        continue

      cj.store()

      text = dat.read()

      # this is for printing the detail status of the case
      if opt_stat == 1:
        contact = re.findall("onclick=\"NewWindow\('(my_contact_info\.jsp\?contact=.+?')",text)

        line = 0
        if len(contact) > 0:
          dat = urllib2.urlopen(urlcm+contact[0])
          contact = re.sub("\s+"," ",dat.read().replace("\n"," ").replace("\r"," "))
          contact = re.sub("</?a(>| href=.+?>)","",contact)
          for desc,value in re.findall("<td class=\"tbcbold\">(.+?):</td>.*?<td class=\"tbc\">(.+?)</td>",contact):
            if line % 2 == 0:
              rowcol = ct.row1
            else:
              rowcol = ct.row2
            txt.ok(ct.style(rowcol,"Contact details - "+str(desc)+": "+str(value).replace("&nbsp;","").strip())+"\n",1)
            line += 1

        for desc,value in re.findall("<b>((?:\w|\s)+?):&nbsp;&nbsp;<\/b>(.+?)</t",text,re.M):
          value = re.sub("<a.+?>.+?</a>"," ",value)
          value = re.sub("<(br|BR)/?>","\n",value,0)
          value = re.sub("<.+?>"," ",value,count=0)
          if line % 2 == 0:
            rowcol = ct.row1
          else:
            rowcol = ct.row2
          txt.ok(ct.style(rowcol,str(desc)+": "+str(value).replace("&nbsp;"," ").strip())+"\n",1)
          line += 1
        continue # we drop out of the loop here

      # this is for uploading files
      if opt_attach == 1:
        try:
          form = fparser.get_form(text,"case_detail")
          dat = urllib2.urlopen(urlcm+"case_attachments.jsp?cid="+form['cid']+"&cobj="+form['cobj']+"&caseOwnerEmail="+form['caseOwnerEmail'])
        except urllib2.URLError as errstr:
          txt.err("while loading the upload form\nERROR: "+str(errstr))
          continue

        text = dat.read()
        fattachparser = FormUpload()
        form = fattachparser.get_form(text,"uploadStatus.jsp")
        print str(form)
        continue # upload has finished

      txt.ok(ct.style(ct.text,"searching for files")+"\r")
      try:
        form = fparser.get_form(text,"case_detail")
        dat = urllib2.urlopen(urlcm+"case_attachments.jsp",urlencode(form))
      except urllib2.URLError:
        txt.err("while searching for case attachments.")
        continue

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
        txt.ok(ct.style(ct.text,"will download to ")+ct.style(ct.fold,str(casedir)+"         ")+"\n")

      maxcmatt = len(attach)
      txt.ok(ct.style(ct.text,"found total of ")+ct.style(ct.num,str(maxcmatt))+ct.style(ct.text," attachment(s) in CM")+"\n")

      filelist = dict()

      curcmatt = 1
      # looping through the attachments
      for att in attach:
        filename = re.search("AttachDown/(.+?)\?OBJID=(.+?)\&",att)
        attfilename = filename.group(1).replace(os.sep,"_").encode('ascii')

        try:
          attsize = int(attssize.pop())
        except IndexError:
          attsize = "?"

        try:
          # attachments upload time is in PST/PDT we need to convert it to local time
          os.environ['TZ'] = "America/Los_Angeles"
          time.tzset()
          atttime = int(time.mktime(time.strptime(attmtime.pop(),"%Y-%m-%d %H:%M:%S")))
          os.environ.pop('TZ')
          time.tzset()

        except:
          atttime = int(time.time())

        # filtering - include
        if not opt_incl == "" and not re.search(opt_incl,attfilename):
            continue

        #filtering - exclude
        if not opt_excl == "" and re.search(opt_excl,attfilename):
            continue

        # download N newest attachments
        if opt_news > 0 and curcmatt <= maxcmatt - opt_news:
            curcmatt += 1
            continue

        # just listing attachments
        if opt_list == 1:

          #txt.ok(ct.style(ct.text,"ObjID: "+str(unquote(filename.group(2)))+"  filename: ")+ct.style(ct.att,str(filename.group(1)))+ct.style(ct.text,"  size: ")+ct.style(ct.num,str(attsize))+ct.style(ct.text," KB  time: ")+ct.style(ct.fold,time.asctime(time.localtime(atttime)))+"\n")
          txt.ok(ct.style(ct.text,"filename: ")+ct.style(ct.att,str(attfilename))+ct.style(ct.text,"  size: ")+ct.style(ct.num,str(attsize))+ct.style(ct.text," KB  time: ")+ct.style(ct.fold,time.asctime(time.localtime(atttime)))+"\n",1)
        else:
          # downloading attachments

          # the names should not repeat
          caseatt = uniqfilename(filelist,str(attfilename))

          # do we overwrite or not?
          if opt_over == 0 and fileexists(casedir+os.sep+caseatt):
            txt.ok(ct.style(ct.text,"file already exists: ")+ct.style(ct.att,str(caseatt))+"\n")
            continue

          # lets make sure that we have the destination directory
          if not os.path.exists(casedir):
            os.makedirs(casedir,mode=0755)

          try:
            #att = quote(att) # this doesn't work anymore
            att = re.sub("\ ","%32",att)
            att = re.sub("\.","%46",att) # this is to encode dot ".", otherwise we get HTTP error 500
            att = urllib2.urlopen(urlcm+att)
          except urllib2.HTTPError as errstr:
            if "302" in str(errstr):
              txt.ok(ct.style(ct.att,str(caseatt))+ct.style(ct.text," - this is probably from SFTP, will get it using FTP")+"\n")
            else:
              txt.warn("HTTP error while downloading "+str(caseatt)+" ERROR:"+str(errstr).replace(os.linesep," "))
            continue

          csize = 0
          try:
            save = open(casedir+os.sep+caseatt,"wb")
            progind = "|"
            stime = time.time()
            lastprint = int(time.time())
            while 1:
              data = att.read(32768)

              if not data:
                break

              save.write(data)
              csize = csize + len(data)

              if lastprint < int(time.time()) and sys.stdout.isatty():
                lastprint = int(time.time())
                progind = progressindicator(progind)
                if attsize == "?":
                  txt.ok(ct.style(ct.ok,"["+str(progind)+"]")+ct.style(ct.text," getting ")+ct.style(ct.att,str(caseatt))+ct.style(ct.text," : ")+ct.style(ct.num,str(csize/1024))+ct.style(ct.text," kB")+(" "*20)+"\r",1)
                else:
                  done = (float(csize)/(attsize*1000))*100
                  if done == 0:
                    eta = "?"
                  else:
                    eta = ts2time(int(((time.time()-stime)/done)*(100-done)))
                  txt.ok(ct.style(ct.ok,"["+str(progind)+"]")+ct.style(ct.text," getting ")+ct.style(ct.att,str(caseatt))+ct.style(ct.text," : ")+ct.style(ct.num,str(csize/1024))+ct.style(ct.text," kB (")+ct.style(ct.num,str(int(done)))+ct.style(ct.text,"% ETA:"+str(eta)+")")+(" "*10)+"\r",1)

            save.close()
            txt.ok(ct.style(ct.text,"download of ")+ct.style(ct.att,str(caseatt))+ct.style(ct.text," size: ")+ct.style(ct.num,str(csize/1024))+ct.style(ct.text," kB done in "+str(ts2time(int(time.time()-stime),1)))+"\n",1)
            os.utime(casedir+os.sep+caseatt,(atttime,atttime))
            if os.name == "posix":
              os.chmod(casedir+os.sep+caseatt,0644)
          except IOError as errstr:
            os.unlink(casedir+caseatt)
            txt.warn("while downloading file: "+ct.style(ct.att,str(caseatt))+" ERROR:"+str(errstr))

      ### FTP SERVER
      if opt_news == 0:

        ### checking ftp upload directory
        try:
          try:
            ftp.cwd("/volume/ftp/pub/incoming/"+caseid)
          except error_temp: # this is to do a relogin if downloading the files from CM takes too long
            ftp = FTP(ftpserver)
            ftp.login(opt_user,opt_fpass)
            ftp.cwd("/volume/ftp/pub/incoming/"+caseid)

          ftpcheck(filelist,caseid,casedir,ftp,opt_incl,opt_excl,opt_list,opt_over)
        except error_perm:
          pass

        ### checking sftp upload directory
        try:
          ftp.cwd("/volume/sftp/pub/incoming/"+caseid)
          ftpcheck(filelist,caseid,casedir,ftp,opt_incl,opt_excl,opt_list,opt_over)
        except error_perm:
          pass

    if opt_news == 0 and opt_stat == 0 and opt_attach == 0:
      ftp.quit()

    cj.store()
  except (KeyboardInterrupt,IOError):
    txt.err("program interrupted, exiting")
    cj.store()
    sys.exit(0)
