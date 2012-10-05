#!/usr/bin/env python

# $Id: 20121005$
# $Date: 2012-10-05 11:37:38$
# $Author: Marek Lukaszuk$

from sgmllib import SGMLParser
from urllib import urlencode,quote
from cookielib import LWPCookieJar
from ftplib import FTP,error_perm,error_temp
from getpass import getpass
import argparse, os, re, sys, time, socket, urllib2, httplib, urlparse, HTMLParser

# the default timeout for all operations
socket.setdefaulttimeout(20)

version = "20121004-dev"

# TODO - make the HTTP connection use keep-alive

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
      txt.ok(ct.style(ct.ok,"["+str(self.ftpprogind)+"]")+ct.style(ct.text," Getting ")+ct.style(ct.att,str(self.ftpatt))+" "+ct.style(ct.num,str(self.fcount/1024))+ct.style(ct.text," kB (")+ct.style(ct.num,str(int(done)))+ct.style(ct.text,"% ETA:"+str(eta)+")")+"        \r",True)

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
    return self.caseid

  def ok(self,mesg,force_print=False):
    '''
    normal messages
    '''
    if arg.quiet == False or force_print == True:
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
  extension of cookie jar class for reusing cookies between sessions
  '''
  def store(self):
    if not self.filename == "":
      try:
        self.save(self.filename,ignore_discard=True,ignore_expires=True)
        if os.name == "posix":
          os.chmod(self.filename,0600)
      except:
        pass

# http://code.activestate.com/recipes/456195/
class MyHTTPConnection(httplib.HTTPConnection):
  def __init__(self, host, port = None):
    print str(host)+" "+str(port)
    urllib2.HTTPConnection.__init__(self, host, port)

  def send(self, s):
    print str(s)
    httplib.HTTPConnection.send(self, s)

  def close(self):
    pass

  def connect(self):
    print "== connecting =="
    urllib2.HTTPConnection.connect(self)

class MyHTTPHandler(urllib2.HTTPHandler):

  def http_open(self, req):
    pass
    urllib2.HTTPHandler.set_http_debuglevel(self, 255)
    return self.do_open(MyHTTPConnection, req)

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
  makes sure that the filenames are unique and encoded correctly
  '''
  filename = filename.decode('ascii','ignore').encode('ascii').replace(os.sep,"_")
  try:
    flist[filename] += 1
  except KeyError:
    flist[filename] = 0
    return filename

  name = re.search("^(.+)(\.\S{1,4})$",filename)
  if name: # if we have extension, then add a number before ext
    return name.group(1)+"_"+str(flist[filename])+name.group(2)
  return filename + "_"+str(flist[filename]) # if we don't see any extension then add the number at the end

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
  return "|"

def ts2time(ts,withseconds=False):
  ts = int(ts)

  asctime = ""
  if ts > 3600:
    asctime = str(ts/3600)+"h "
    ts = ts % 3600
  if ts > 60:
    asctime += str(ts/60)+"m "
    ts = ts % 60
  if withseconds == True or asctime == "":
    return asctime+str(ts)+"s"
  return asctime

def ftpcheck(filelist,caseid,lcasedir,ftp,include,exclude,list,over):
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

    try: # this checks if we have directories, if we do we go recursive
      ftp.cwd(filename)
      ftpcheck(filelist,caseid,lcasedir+os.sep+filename,ftp,include,exclude,list,over)
      ftp.cwd("..")
      continue
    except error_perm:
      pass

    if not include == "" and not re.search(include,filename):
      continue

    if not exclude == "" and re.search(exclude,filename):
      continue

    if list == True:
      ftp.sendcmd("TYPE i")
      txt.ok(ct.style(ct.text,"filename: ")+ct.style(ct.att,str(filename))+ct.style(ct.text," size: ")+ct.style(ct.num,str(int(ftp.size(str(filename)))/1024))+ct.style(ct.text," kB")+"\n",True)
      continue

    try:
      atttime = time.mktime(time.strptime((str(ftp.sendcmd("MDTM "+filename)).split())[1],"%Y%m%d%H%M%S"))
    except:
      atttime = time.time()

    ftpatt = uniqfilename(filelist,str(filename))

    # do we overwrite or not?
    if over == False and fileexists(lcasedir+os.sep+ftpatt):
      txt.ok(ct.style(ct.text,"file already exists: ")+ct.style(ct.att,str(ftpatt))+"\n")
      continue

    if not os.path.exists(lcasedir):
      os.makedirs(lcasedir,mode=0755)

    txt.ok(ct.style(ct.text,"downloading ")+ct.style(ct.att,str(ftpatt))+"\r",True)
    try:
      ftpfile = open(lcasedir+os.sep+str(ftpatt),"wb")
      ftp.sendcmd("TYPE i")
      ftpstime = time.time()
      ftpcb = ftpcallback(ftpatt, ftpfile, ftp.size(filename), ftpstime)
      ftp.retrbinary("RETR "+filename,ftpcb.main,blocksize=32768)
      ftpfile.close()
      fcount = ftpcb.fcount
    except:
      os.unlink(lcasedir+os.sep+ftpatt)
      txt.warn("error while downloading file: "+ct.style(ct.att,str(ftpatt)))
      continue

    txt.ok(ct.style(ct.text,"download of ")+ct.style(ct.att,str(ftpatt))+ct.style(ct.text," size: ")+ct.style(ct.num,str(fcount/1024))+ct.style(ct.text," kB done in "+str(ts2time(int(time.time()-ftpstime),1)))+"\n",True)
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
      opt_dir = os.curdir
      pass

    # by default we use colors
    ct = color_theme()

    parser = argparse.ArgumentParser(formatter_class=argparse.RawDescriptionHelpFormatter,
        description="\
  Author: Marek Lukaszuk\n\
  Version: "+str(version)+"\n",epilog="\
  You can define the user, password and the download directory in a file\n\
  "+str(os.environ['HOME'])+"/.cm.conf\n\
  which should look like this:\n\
  cmuser=YOUR_USERNAME_FOR_CM\n\
  cmpass=YOUR_PASSWORD_FOR_CM\n\
  cmdir=THE_MAIN_DIRECTORY_WHERE_TO_DOWNLOAD_ATTACHMENTS")

    group_attach = parser.add_argument_group('Attachments')
    group_attach.add_argument('-a','--attach',default=[],action='append',help='attach file to the case')
    group_attach.add_argument('-d','--directory',default=opt_dir,help='directory where to download attachments,inside that directory a directory with the case number will be created. If not provided the value from the config file will be used, if the config file is not there the current directory will be used')
    group_attach.add_argument('-e','--exclude',default="",help='(exclude) skip downloading or listing attachments which filenames match regexp')
    group_attach.add_argument('-i','--include',default="",help='(include) download or list only attachments which filenames match regexp. If specified together with --exclude the --include regexp is matched first')
    group_attach.add_argument('-l','--list',action='store_true',help='just list case attachments without downloading,')
    group_attach.add_argument('-n','--newest',type=int,default=0,help='number of newest attachments to download/list from CM, this will skip FTP and SFTP')
    group_attach.add_argument('-nd','--no-dir',action='store_true',help='don\'t create the case directory just dump everything into root of the specified directory')
    group_attach.add_argument('-o','--overwrite',action='store_true',help='force overwrite of the files')
    group_attach.add_argument('-t','--temp-folder',action='store_true',help='this will download attachments to a folder "temp" in the destination folder (for cases that you just want to look at)')
    group_case = parser.add_argument_group('Case info')
    group_case.add_argument('-s','--status',action='store_true',help='show case status, customer information and exit, don\'t download anything')
    group_case.add_argument('-cn','--case-notes',action='store_true',help='show case notes and exit, don\'t download anything')
    group_auth = parser.add_argument_group('Authentication')
    group_auth.add_argument('-u','--user',default=opt_user,help='user name used for the CM')
    group_auth.add_argument('-p','--passwd',default=opt_pass,help='password used for the CM')
    group_auth.add_argument('-fp','--ftp-passwd',default=opt_pass,help='password used for ftp (if not set this will be the same as -p),if value of this will be \"0\" then you will be asked for the password')
    group_color = parser.add_argument_group('Colors')
    group_color.add_argument('-bbg','--bright-background-color',action='store_true',help='bright background (different color theme)')
    group_color.add_argument('-dc','--disable-colors',action='store_true',help='disable colors')
    parser.add_argument('-q','--quiet',action='store_true',help='be quiet, print only information when a file is downloaded')
    parser.add_argument('-v','--version',action='version', version="%(prog)s "+str(version))
    parser.add_argument('caseid',nargs='+',default=[],help="Case ID - if not provided script will check if the current folder name starts with something that looks like a case id, if yes then it will be used");

    (arg,rest_argv) = parser.parse_known_args(sys.argv)

    # setting colors
    if arg.bright_background_color == True:
      ct = bbg_theme()

    if arg.disable_colors == True:
      ct = nocolor_theme()

    if not sys.stdout.isatty():
      ct = nocolor_theme()
      arg.quiet = True

    cases = {}
    for cid in arg.caseid+rest_argv:
      if re.match("^\d{4}-\d{4}-\d{4}$",cid):
        cases[cid] = 1

    txt = msg() # class object for the messages printing

    opt_ucwd = False
    if len(cases) == 0:
      m = re.match("^\d{4}-\d{4}-\d{4}",os.path.basename(os.getcwd()))
      if m != None:
        cases[m.group(0)] = 1
        arg.directory = ""
        opt_ucwd = True

    # just to check we have enough information to go further
    if len(cases) == 0 or arg.user == "":
      txt.err("either case id or user name was not defined")
      sys.exit(1)

    # here we start the actual connection
    cj = cookiemonster(filename=cookiefile)
    try:
      cj.load(ignore_discard=True, ignore_expires=True)
    except IOError:
      pass

#    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#    url = urlparse.urlparse(urlcm)
#    sock.connect((socket.gethostbyname(url[1]),int(socket.getservbyname(url[0]))))

    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
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
      if arg.passwd == "":
        try:
          arg.passwd = getpass("Please enter password: ").strip()
        except:
          usage()

      if arg.passwd == "":
        txt.err("password can not be empty")
        sys.exit(1)

    # ftp password
    if arg.ftp_passwd == "0":
      try:
        arg.ftp_passwd = getpass("Please enter FTP password: ").strip()
      except:
        usage()

    if arg.ftp_passwd == "":
      arg.ftp_passwd = arg.passwd

    if not "Case Management Home" in text:
      txt.ok(ct.style(ct.text,"logging into the CM")+"\r")
      try:
        form = fparser.get_form(text,"Login")
        form['login'] = arg.user
        form['password'] = arg.passwd
        dat = urllib2.urlopen(dat.geturl(),urlencode(form))
      except urllib2.URLError as errstr:
        txt.err("can't log into CM,\nERROR:"+str(errstr))
        sys.exit(1)

    txt.ok(ct.style(ct.text,"in the CM")+"\r")

    mainpage = dat.read()

    if "Login Error" in mainpage:
      txt.err("wrong credentials for CM.")
      sys.exit(1)

    if arg.case_notes == False and arg.newest == 0 and arg.status == False and len(arg.attach) == 0:
      txt.ok(ct.style(ct.text,"logging into ftp server")+"\r")
      # trying to login to the ftp server
      try:
        ftp = FTP(ftpserver)
        ftp.login(arg.user,arg.ftp_passwd)
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
      if arg.status == True:
        text = text.replace("\n"," ").replace("\r"," ")

        contact = re.findall("onclick=\"NewWindow\('(my_contact_info\.jsp\?contact=.+?')",text)

        line = 0
        if len(contact) > 0:
          dat = urllib2.urlopen(urlcm+contact[0])
          contact = re.sub("\s+"," ",dat.read().replace("\n"," ").replace("\r"," "))
          contact = re.sub("</?a(>| href=.+?>)","",contact)
          for desc,value in re.findall("<td class=\"tbcbold\">(.+?):</td>.*?<td class=\"tbc\">(.+?)</td>",contact):
            rowcol = ct.row1
            if line % 2 == 0:
              rowcol = ct.row2
            txt.ok(ct.style(rowcol,"Contact details - "+str(desc)+": "+str(value).replace("&nbsp;","").strip())+"\n",True)
            line += 1

        for desc,value in re.findall("<b>((?:\w|\s)+?):&nbsp;&nbsp;<\/b>(.+?)</t",text,flags=re.M):
          value = re.sub("<a.+?>.+?</a>"," ",value)
          value = re.sub("<(br|BR)/?>","\n",value,0)
          value = re.sub("<.+?>"," ",value,count=0)
          rowcol = ct.row1
          if line % 2 == 0:
            rowcol = ct.row2
          txt.ok(ct.style(rowcol,str(desc)+": "+str(value).replace("&nbsp;"," ").strip())+"\n",True)
          line += 1
        continue # we drop out of the loop here

      # printing detail case notes
      if arg.case_notes == True:
        print ""
        try:
          form = fparser.get_form(text,"case_detail")
          dat = urllib2.urlopen(urlcm+"case_all_note_details.jsp?cid="+quote(form['cid'])+"&cobj="+quote(form['cobj'])+"&caseOwnerEmail="+quote(form['caseOwnerEmail']))
        except urllib2.URLError as errstr:
          txt.err("while loading the case notes\nERROR: "+str(errstr))
          continue

        h = HTMLParser.HTMLParser()
        text = re.sub("[ \t\n\r\f\v]+"," ",dat.read(),flags=re.M)
        text = re.sub("(</?br>)+","<br>",text,flags=re.I)
        notes = re.findall("<tr valign=\"top\">(.+?)</tr>",text)
        line = 0
        for note in notes:
          note = re.sub("</?br>","\n",note,flags=re.I+re.M)
          note = re.sub("<.+?>","",note)
          rowcol = ct.row1
          if line % 2 == 0:
            rowcol = ct.row2
          print ct.style(rowcol,str(h.unescape(note.decode('ascii','ignore'))))+"\n\n"+"#%"*37+"\n\n"
          line += 1
        continue # we drop out of the loop here

      # uploading files
      if len(arg.attach) > 0:
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

      arg.directory = arg.directory.rstrip(os.sep)
      casedir = str(arg.directory)+os.sep+str(caseid)+os.sep

      if arg.temp_folder == True:
        casedir = str(arg.directory)+os.sep+"temp"+os.sep+str(caseid)+os.sep

      if opt_ucwd == True:
        casedir = os.curdir+os.sep

      if arg.no_dir == True:
        casedir = str(arg.directory)+os.sep

      casedir = os.path.normpath(casedir)
      if arg.list == False:
        txt.ok(ct.style(ct.text,"will download to ")+ct.style(ct.fold,str(casedir)+"         ")+"\n")

      maxcmatt = len(attach)
      txt.ok(ct.style(ct.text,"found total of ")+ct.style(ct.num,str(maxcmatt))+ct.style(ct.text," attachment(s) in CM")+"\n")

      filelist = dict()

      curcmatt = 1
      # looping through the attachments
      for att in attach:
        filename = re.search("AttachDown/(.+?)\?OBJID=(.+?)\&",att)
        attfilename = filename.group(1)

        try:
          attsize = int(attssize.pop())
        except IndexError:
          attsize = "?"

        try: # attachments upload time is in PST/PDT we need to convert it to local time
          os.environ['TZ'] = "America/Los_Angeles"
          time.tzset()
          atttime = int(time.mktime(time.strptime(attmtime.pop(),"%Y-%m-%d %H:%M:%S")))
          os.environ.pop('TZ')
          time.tzset()
        except:
          atttime = int(time.time())

        # filtering - include
        if not arg.include == "" and not re.search(arg.include,attfilename):
          continue

        # filtering - exclude
        if not arg.exclude == "" and re.search(arg.exclude,attfilename):
          continue

        # download N newest attachments
        if arg.newest > 0 and curcmatt <= maxcmatt - arg.newest:
          curcmatt += 1
          continue

        # just listing attachments
        if arg.list == True:

          txt.ok(ct.style(ct.text,"filename: ")+ct.style(ct.att,str(attfilename))+ct.style(ct.text,"  size: ")+ct.style(ct.num,str(attsize))+ct.style(ct.text," KB  time: ")+ct.style(ct.fold,time.asctime(time.localtime(atttime)))+"\n",True)
        else:
          # downloading attachments

          # the names should not repeat
          caseatt = uniqfilename(filelist,str(attfilename))

          # do we overwrite or not?
          if arg.overwrite == 0 and fileexists(casedir+os.sep+caseatt):
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
                  txt.ok(ct.style(ct.ok,"["+str(progind)+"]")+ct.style(ct.text," getting ")+ct.style(ct.att,str(caseatt))+ct.style(ct.text," : ")+ct.style(ct.num,str(csize/1024))+ct.style(ct.text," kB")+(" "*20)+"\r",True)
                else:
                  done = (float(csize)/(attsize*1000))*100
                  if done == 0:
                    eta = "?"
                  else:
                    eta = ts2time(int(((time.time()-stime)/done)*(100-done)))
                  txt.ok(ct.style(ct.ok,"["+str(progind)+"]")+ct.style(ct.text," getting ")+ct.style(ct.att,str(caseatt))+ct.style(ct.text," : ")+ct.style(ct.num,str(csize/1024))+ct.style(ct.text," kB (")+ct.style(ct.num,str(int(done)))+ct.style(ct.text,"% ETA:"+str(eta)+")")+(" "*10)+"\r",True)

            save.close()
            txt.ok(ct.style(ct.text,"download of ")+ct.style(ct.att,str(caseatt))+ct.style(ct.text," size: ")+ct.style(ct.num,str(csize/1024))+ct.style(ct.text," kB done in "+str(ts2time(int(time.time()-stime),1)))+"\n",True)
            os.utime(casedir+os.sep+caseatt,(atttime,atttime))
            if os.name == "posix":
              os.chmod(casedir+os.sep+caseatt,0644)
          except IOError as errstr:
            os.unlink(casedir+caseatt)
            txt.warn("while downloading file: "+ct.style(ct.att,str(caseatt))+" ERROR:"+str(errstr))

      ### FTP SERVER
      if arg.newest == 0:

        ### checking ftp upload directory
        try:
          try:
            ftp.cwd("/volume/ftp/pub/incoming/"+caseid)
          except error_temp: # this is to do a relogin if downloading the files from CM takes too long
            ftp = FTP(ftpserver)
            ftp.login(arg.user,arg.ftp_passwd)
            ftp.cwd("/volume/ftp/pub/incoming/"+caseid)

          ftpcheck(filelist,caseid,casedir,ftp,arg.include,arg.exclude,arg.list,arg.overwrite)
        except error_perm:
          pass

        ### checking sftp upload directory
        try:
          ftp.cwd("/volume/sftp/pub/incoming/"+caseid)
          ftpcheck(filelist,caseid,casedir,ftp,arg.include,arg.exclude,arg.list,arg.overwrite)
        except error_perm:
          pass

    if arg.case_notes == False and arg.newest == 0 and arg.status == False and len(arg.attach) == 0:
      ftp.quit()

    cj.store()
  except (KeyboardInterrupt,IOError):
    txt.err("program interrupted, exiting")
    cj.store()
    sys.exit(0)
