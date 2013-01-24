
# $Id: 20130109$
# $Date: 2013-01-09 21:08:44$
# $Author: Marek Lukaszuk$

# you need to install this in ~/.gg/scripts/
# documentation for the ekg modules is in:
# http://ekg.chmurka.net/docs/python.txt

import ekg
import re,os,time

urllogfile = os.environ['HOME']+"/.gg/urllog.txt"

def urlsave(ts,name,urls):
  for url in urls:

    open(urllogfile,"a").write(str(time.strftime("%Y-%m-%d_%H:%M:%S",time.localtime(ts)))+" "+str(name)+" "+str(url)+"\n")
    ekg.printf("generic","url saved: "+str(url))

def init():
  ekg.printf("generic","url grabber loaded")

  return 1

def deinit():
  ekg.printf("generic","url grabber says bye, bye")

def handle_msg(uin, name, msgclass, text, ts, secure):
  urls = re.findall("(?:^|\s)(\S+://\S+)(?:\s|$)",text)
  if urls:
    urlsave(ts,name,urls)

  return 1

def handle_msg_own(rcpts, text):
  urls = re.findall("(?:^|\s)(\S+://\S+)(?:\s|$)",text)
  if urls:
    urlsave(int(time.time()),"ja",urls)

  return 1

def handle_command_line(target, line):
  if "/urllist" in line:
    try:
      for line in open(urllogfile).read().split("\n"):
        ekg.printf("generic",line)
    except:
      pass
