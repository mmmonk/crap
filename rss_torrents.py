#!/usr/bin/env python

import httplib
import feedparser
import re
import os

RSSFEEDS = ( 
  'http://www.ebookshare.net/plus/rss/index.xml',
  #'http://rss.bt-chat.com/?group=3&cat=9',
  'http://rss.bt-chat.com/?group=4'
  ) 

RSSDOWNLOAD = {
  'http://www.ebookshare.net/plus/rss/index.xml': ['http://(.+?)/.+-(\d+)\.html','http://\g<1>/download.php?id=\g<2>']
  }

TORRENTSDIR = '/home/case/Desktop/torrents/'
DATAFILE = TORRENTSDIR+'rss_torrents.dat'
DATATMPFILE = TORRENTSDIR+'rss_torrents.tmp'

DEBUG=1

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
  '''
  return a.replace('\n','')

def LoadDataFile(file):
  '''
  loads the data file with the list of already seen torrents
  '''

  global SEENTORRENTS

  DbPrint('Loading data file '+file)

  try:
	datafile = open(file,'r')
  except:
	DbPrint('No old data file present',0)
	return

  SEENTORRENTS = map(MapNewLineClean,datafile.readlines())

  datafile.close()  

def GetFile(url):
  '''
  Function - get the file specified by the url (used inside ReadFeed)
  input: url of the file to download

  '''
  if 'http://' in url:
	url = url.replace('http://','',1)


  if url in SEENTORRENTS:
	DbPrint('Already seen torrent ('+url+')')
	return

  # url[0] - hostname
  # url[2] - file path part of url
  url = url.partition('/')

  DbPrint('connecting to '+url[0]+'/'+url[2])

  http_connection = httplib.HTTPConnection(url[0],80,5)
  http_connection.request('GET',"/"+url[2])
  http_response = http_connection.getresponse();
  http_connection.close()

  DbPrint('response from '+url[0]+'/'+url[2]+' is "'+repr(http_response.status)+' '+http_response.reason+'" and it is '+http_response.getheader('Content-Type'))

  if http_response.status != 200:
	DbPrint('HTTP response not 200, ignoring link',1)
	return

  # if this is not bittorrent file then we are not intrested
  if 'x-bittorrent'not in http_response.getheader('Content-Type'):
	DbPrint('not bittorrent file, ignore',1)
	return

  # first use the last part of the url for the filename
  filename = (url[2].rpartition('/'))[2]

  if '\.torrent' not in filename:
	filename = filename+'.torrent'

  # then check if the server send us Content-Disposition header with the filename
  if 'filename' in http_response.getheader('Content-Disposition'):
	filename = (http_response.getheader('Content-Disposition').rpartition('='))[2]
  
  filename = filename.lower().replace(' ','_').strip('?\/*+!"')

  DbPrint('saving torrent '+url[0]+'/'+url[2]+' to file '+TORRENTSDIR+filename)

  try:
	open(TORRENTSDIR+filename,'r')
	DbPrint('torrent file already exists',1)
	return
  except:
	pass

  torrent = open(TORRENTSDIR+filename,'wb')
  torrent.write(http_response.read());
  torrent.close()

  datatmpfile = open(DATATMPFILE,'a')
  datatmpfile.write(url[0]+'/'+url[2]+'\n')
  datatmpfile.close()

def ReadFeed(url):
  ''' 
  reads RSS feed, filters for intresting things and gets the links to the torrent files
  input: url to the RSS feed

  '''
  DbPrint('connecting to RSS feed '+url)

  rssfeed = feedparser.parse(url)

  for rssentry in rssfeed.entries:
	DbPrint('---------------------- start new link ----------------------')
	DbPrint('torrent title - "'+rssentry.title+'"')
	link = rssentry.link

	if url in RSSDOWNLOAD:
	  DbPrint('feed in the RSSDOWNLOAD list')
	  DbPrint('  orginal link '+rssentry.link)
	  rssentry.link = re.sub(RSSDOWNLOAD[url][0],RSSDOWNLOAD[url][1],rssentry.link)
	  DbPrint('  new link '+rssentry.link)
	
	GetFile(rssentry.link)


if __name__ == '__main__':

  LoadDataFile(DATAFILE)

  for feed in RSSFEEDS:
	ReadFeed(feed)
  
  try:
	open(DATATMPFILE,'r')
	os.rename(DATATMPFILE,DATAFILE)
  except:
	pass  
