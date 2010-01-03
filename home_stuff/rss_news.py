#!/usr/bin/env python
"""
Author: <m.lukaszuk(at)gmail.com> 2010

Script to news from RSS feeds via email feeds
"""
import httplib
import feedparser
import re
import os 
import time 
import random
import socket
import smtplib

# dictionary of lists of how we need to transform the link from the host to get the link to the RSSNEWS file 
RSSDOWNLOAD = { }

# dictionary of lists of what we are intrested in specific feeds 
RSSALLOW = { }

# dictionary of lists of what we are not intrested in specific feeds
RSSDENY = { }

RSSNEWSSDIR = '/home/guest/case/'
FEEDSFILE = RSSNEWSSDIR+'.rss_news.feeds'
DATAFILE = RSSNEWSSDIR+'.rss_news.dat'
DATATMPFILE = RSSNEWSSDIR+'.rss_news.tmp'

# time in minutes, not yet used
HOWOFTENTOCHECK = 45

# global socket timeout in seconds (used in httplib)
timeout = 10
socket.setdefaulttimeout(timeout)

DEBUG=0

HTTPHEADERS = {
  'User-Agent':	'Mozilla/5.0 (Windows; U; Windows NT 5.1; en; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3',
  'Connection': 'close'
}

me = 'm.lukaszuk@gmail.com'

############################# FUNCTIONS #############################

def DbPrint(debugstr,errorvar=0):
  ''' 
  Function - print debugs if variable DEBUG is set to 1 
  input: string to print
  '''
  if DEBUG == 1:
	errorsign = '+'
	if errorvar == 1:
	  errorsign = '-'
	
	print '[%c] %s' % (errorsign,debugstr)

def MapNewLineClean(a):
  '''
  removes new line characters from the loaded data file in LoadDataFile
  input: string
  output: string with out a new line character
  '''
  return a.replace('\n','')


def AddToDataFile(url):
  '''
  adds url to the temporary data file
  intput: url of the RSSNEWS file that we have already downloaded
  '''
  try: 
	datatmpfile = open(DATATMPFILE,'a')
	datatmpfile.write(url+'\n')
	datatmpfile.close()
  except:
	DbPrint('error while writing '+DATATMPFILE,1)
	os._exit(os.EX_CANTCREAT)

def LoadDataFile(file):
  '''
  loads the data file with the list of already seen RSSNEWSs, populates SEENRSSNEWSS variable
  input: file containing a list of urls of already seen RSSNEWSs
  '''

  global SEENRSSNEWSS

  SEENRSSNEWSS = [ ]

  DbPrint('Loading data file '+file)

  try:
	datafile = open(file,'r')
  except:
	DbPrint('No old data file present',0)
	return

  SEENRSSNEWSS = map(MapNewLineClean,datafile.readlines())

  datafile.close()  

def LoadFeeds(file):

  global RSSFEEDS
  
  DbPrint('Loading feeds file '+file)
  
  try:
	feedsfile = open(file,'r')
  except:
	DbPrint('No feeds file present',1)
	return 0 
					
  RSSFEEDS = map(MapNewLineClean,feedsfile.readlines())
	
  feedsfile.close()
  return 1 

def ReadFeed(url):
  ''' 
  reads RSS feed, filters for intresting things and gets the links to the RSSNEWS files
  input: url to the RSS feed

  '''
  DbPrint('connecting to RSS feed '+url)

  if 'http://' in url:
    host = url.replace('http://','',1)

  i = host.find('/')
  if i >= 0:
    host = host[:i]

  try:
    rssfeed = feedparser.parse(url)
  except:
    DbPrint('Connection problems')
    for RSSNEWSlink in SEENRSSNEWSS:
      if host in RSSNEWSlink:
            AddToDataFile(RSSNEWSlink)
    return

  for rssentry in rssfeed.entries:
	if rssentry.link in SEENRSSNEWSS:
	  AddToDataFile(rssentry.link)
	else:
	  DbPrint('---------------------- start new link ----------------------')
	  DbPrint('title - "'+rssentry.title.encode(rssfeed.encoding,'ignore')+'"')

	  msg = "To: <%s>\n" % me 
	  msg += "Content-Type: text/html; charset=\"%s\"\n" % rssfeed.encoding
#          msg += "MIME-Version: 1.0\n"
	  msg += "Content-Transfer-Encoding: 8bit\n"
	  msg += "Subject: rss2mail: %s - %s\n" % (rssfeed.feed.title,rssentry.title)
	  msg += "From: <%s>\n\n" % me 
	  msg += rssentry.description
	  msg += "\npostlink: %s\n" % rssentry.link

	  try:
		s = smtplib.SMTP('127.0.0.1','25','localhost')
		s.sendmail(me, [me], msg.encode(rssfeed.encoding,'ignore'))
		s.quit()
		AddToDataFile(rssentry.link)
		DbPrint('message send ok')
	  except:
		DbPrint('message send not ok')

	  time.sleep(1)

#####################################################################

if __name__ == '__main__':

  random.seed()

  feedparser.USER_AGENT = HTTPHEADERS['User-Agent']
  if LoadFeeds(FEEDSFILE):
	LoadDataFile(DATAFILE)


	try:
	  for feed in RSSFEEDS:
		sleeptime=random.randint(2,15)
		DbPrint('sleeping for '+str(sleeptime)+' seconds')
		time.sleep(sleeptime)
		DbPrint('====================== start new feed ======================')
		ReadFeed(feed)

	except: 
	  DbPrint('interupted exiting')
   
	try:
	  tempfile = open(DATATMPFILE,'r')
	  tempfile.close()
	  os.rename(DATATMPFILE,DATAFILE)
	except:
	  pass
