#!/usr/bin/env python

# $Id: 20130207$
# $Date: 2013-02-07 14:39:01$
# $Author: Marek Lukaszuk$

import pymongo
import sys, os, time, smtplib

home = os.environ['HOME']

ircurlfile = home+"/.irssi/url"
ggurlfile = home+"/.gg/urllog.txt"
twurlfile = home+"/.twitter_url_log.txt"

ignorelist = (
  "://www.youtube.com/",
  "://youtu.be/",
  "://pastebin.",
  "://pastebay",
  "://pastie.org",
  "://lmgtfy.com",
  "://www.lmgtfy.com"
  )

def mongocheck(newlinks,urls,source,user,url):
  if urls.find({'_id': url}).count() > 0:
    urls.update({"_id": url},{"ts":int(time.time())})
  else:
    if urls.find({'_id': url.lower()}).count() > 0:
      urls.update({"_id": url.lower()},{"ts":int(time.time())})
    else:
      good = True
      for ignore in ignorelist:
        if ignore in url:
          good = False
          break

      if good == True:
        newlinks[url] = source+" "+user

  return newlinks


if __name__ == '__main__':

  newlinks = {}

  try:
    connection = pymongo.Connection()
  except:
    print "Problem with connecting to the mongoDB"
    sys.exit(1)

  db = connection.urls
  urls = db['urls']

  ## twitter url logs
  if os.path.isfile(twurlfile) and os.stat(twurlfile).st_size > 0:
    for line in open(twurlfile,'r').readlines():
      line = line.strip()
      linea = line.split()

      newlinks = mongocheck(newlinks,urls,"twitter",linea[1],linea[0])

  ## gg url logs
  if os.path.isfile(ggurlfile) and os.stat(ggurlfile).st_size > 0:
    for line in open(ggurlfile,'r').readlines():
      line = line.strip()
      linea = line.split()

      newlinks = mongocheck(newlinks,urls,"gg",linea[1],linea[2])

  ## irc logs
  if os.path.isfile(ircurlfile) and os.stat(ircurlfile).st_size > 0:
    for line in open(ircurlfile,'r').readlines():
      line = line.strip()
      line = line.strip(",.")
      linea = line.split()

      if "://" not in linea[9]:
        continue

      newlinks = mongocheck(newlinks,urls,linea[8],linea[7],linea[9])

  ## send out the email
  if len(newlinks) > 0:

    msg = "From: marek@mmmonk.net\nTo: m.lukaszuk@gmail.com\nSubject: urls from logs - "+(time.strftime("%Y/%m/%d %H:%M:%S",time.localtime()))+"\n\n"
    for link,channel in sorted(newlinks.items(), key=lambda x: x[0].replace("//www.","//",1).split(":")[1]):
      msg += link+" "+channel+"\n"

    smtpObj = smtplib.SMTP("127.0.0.1")
    smtpObj.sendmail('m.lukaszuk@gmail.com','m.lukaszuk@gmail.com',msg)

    for link,channel in newlinks.items():
      item = {'_id': link, 'ts': int(time.time())}
      urls.insert(item)

#    if os.path.isfile(ircurlfile) and os.stat(ircurlfile).st_size > 0:
#      os.unlink(ircurlfile)
#    if os.path.isfile(ggurlfile) and os.stat(ggurlfile).st_size > 0:
#      os.unlink(ggurlfile)
#    if os.path.isfile(twurlfile) and os.stat(twurlfile).st_size > 0:
#      os.unlink(twurlfile)
