#!/usr/bin/env python
"""
Author: <m.lukaszuk(at)gmail.com> 2009

Script to download torrents from RSS feeds with filtering for only intresting ones ;)
"""
import httplib
import feedparser
import re
import os 
import time 
import random
import socket

# list of RSS feeds that we are intrested in
RSSFEEDS = [
  'http://www.ezrss.it/search/index.php?show_name=house&show_name_exact=true&date=&quality=&release_group=&mode=rss',
  'http://www.ezrss.it/search/index.php?show_name=lie+to+me&show_name_exact=true&date=&quality=&release_group=&mode=rss',
  'http://www.ebookshare.net/plus/rss/index.xml'
  ] 

# dictionary of lists of how we need to transform the link from the host to get the link to the torrent file 
RSSDOWNLOAD = {
  'www.ebookshare.net': ['http://(.+?)/.+-(\d+)\.html','http://\g<1>/download.php?id=\g<2>'],
  'www.mininova.org': ['http://(.+?)/tor/(\d+)','http://\g<1>/get/\g<2>']  
  }

# dictionary of lists of what we are intrested in specific feeds 
RSSALLOW = {
  'http://www.ebookshare.net/plus/rss/index.xml': ['-lib','ebook-','scientist','science','popular mechanics'],
  }

# dictionary of lists of what we are not intrested in specific feeds
RSSDENY = {
  'http://www.ebookshare.net/plus/rss/index.xml': ['microsoft office','religion','social','history','sharepoint','visual basic','dot net','sql','ado net','active directory','photoshop','adobe','rowman','routledge','windows 7','interface design','corporate power','web technologies','information technologies','blender','joomla','xhtml',' mac ','drupal'],
  'http://www.ezrss.it/search/index.php?show_name=house&show_name_exact=true&date=&quality=&release_group=&mode=rss' : ['720p - hdtv']
  }


TORRENTSDIR = '/home/case/Desktop/torrents/'
DATAFILE = TORRENTSDIR+'rss_torrents.dat'
DATATMPFILE = TORRENTSDIR+'rss_torrents.tmp'

# time in minutes, not yet used
HOWOFTENTOCHECK = 45

# global socket timeout in seconds (used in httplib)
timeout = 10
socket.setdefaulttimeout(timeout)

DEBUG=1

HTTPHEADERS = {
  'User-Agent':	'Mozilla/5.0 (Windows; U; Windows NT 5.1; en; rv:1.8.1.3) Gecko/20070309 Firefox/2.0.0.3',
  'Connection': 'close'
}


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
  intput: url of the torrent file that we have already downloaded
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
  loads the data file with the list of already seen torrents, populates SEENTORRENTS variable
  input: file containing a list of urls of already seen torrents
  '''

  global SEENTORRENTS

  SEENTORRENTS = [ ]

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
	DbPrint('already seen torrent ('+url+')')
	AddToDataFile(url)	
	return

  # url[0] - hostname
  # url[2] - file path part of url
  url = url.partition('/')

  DbPrint('connecting to '+url[0]+'/'+url[2])

  HTTPHEADERS['Host'] = url[0]

  http_connection = httplib.HTTPConnection(url[0])
  http_connection.request('GET',"/"+url[2],'',HTTPHEADERS)
  
  try:
	http_response = http_connection.getresponse();
  except: 
	DbPrint('Connection timed out')
	return

  data = http_response.read()
  http_connection.close()

  if not len(data) > 0:
	DbPrint('length of the response is 0')
	return

  try:
    DbPrint('response is "'+repr(http_response.status)+' '+http_response.reason+'" and it is '+http_response.getheader('Content-Type'))
  except:
    pass

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
  try:
    if http_response.getheader('Content-Disposition') and 'filename' in http_response.getheader('Content-Disposition'):
          filename = (http_response.getheader('Content-Disposition').rpartition('='))[2]
  except:
    pass 

  try:
	filename = str(filename)
  except UnicodeEncodeError:
	filename = filename.encode('ascii', 'ignore')

  filename = filename.lower().replace(' ','_').strip('?\/*+!"')

  DbPrint('saving torrent to file '+TORRENTSDIR+filename)

  try:
	open(TORRENTSDIR+filename,'r')
	DbPrint('torrent file already exists',1)
	return
  except:
	pass

  try:
	torrent = open(TORRENTSDIR+filename,'wb')
	torrent.write(data);
	torrent.close()
	DbPrint('  completed')
	AddToDataFile(url[0]+'/'+url[2])

  except:
	DbPrint('  error while saving',1)
	
def ReadFeed(url):
  ''' 
  reads RSS feed, filters for intresting things and gets the links to the torrent files
  input: url to the RSS feed

  '''
  DbPrint('connecting to RSS feed '+url)

  if 'http://' in url:
    host = url.replace('http://','',1)

  host = (host.partition('/'))[0]

  try:
	rssfeed = feedparser.parse(url)
  except:
	DbPrint('Connection problems')
	for torrentlink in SEENTORRENTS:
	  if host in torrentlink:
		AddToDataFile(torrentlink)
	return

  for rssentry in rssfeed.entries:
	DbPrint('---------------------- start new link ----------------------')
	DbPrint('torrent title - "'+rssentry.title+'"')

	title = rssentry.title.lower()

	DbPrint('torrent title for checking against the filters - "'+title+'"')

	torrentdenied = False

	if url in RSSALLOW:
	  DbPrint('feed in RSSALLOW')
	  for text in RSSALLOW[url]:
  		if text not in title: 
		  torrentdenied = True
		else:
		  torrentdenied = False
		  break

	if url in RSSDENY and not torrentdenied:
	  DbPrint('feed in RSSDENY:')
	  for text in RSSDENY[url]:
		if text in title: 
		  torrentdenied = True
		  break
		else:
		  torrentdenied = False

	if not torrentdenied:
	  pass
	  if host in RSSDOWNLOAD:
		DbPrint('host in the RSSDOWNLOAD list')
		DbPrint('  orginal link '+rssentry.link)
		rssentry.link = re.sub(RSSDOWNLOAD[host][0],RSSDOWNLOAD[host][1],rssentry.link)
		DbPrint('  new link '+rssentry.link)
	  
	  GetFile(rssentry.link)
	else:
	  DbPrint('not intrested in this torrent')



#####################################################################

if __name__ == '__main__':

  random.seed()

  feedparser.USER_AGENT = HTTPHEADERS['User-Agent']
  LoadDataFile(DATAFILE)

  try:
	for feed in RSSFEEDS:
	  DbPrint('====================== start new feed ======================')
	  ReadFeed(feed)
	  sleeptime=random.randint(2,15)
	  DbPrint('sleeping for '+str(sleeptime)+' seconds')
	  time.sleep(sleeptime)

  except KeyboardInterrupt:
	DbPrint('CTRL+C pressed, exiting')
 
  try:
	tempfile = open(DATATMPFILE,'r')
        tempfile.close()
        os.rename(DATATMPFILE,DATAFILE)
  except:
	pass
