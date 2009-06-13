#!/usr/bin/env python

import httplib
import feedparser
import re

RSSFEEDS = ( 
  'http://www.ebookshare.net/plus/rss/index.xml',
  #'http://rss.bt-chat.com/?group=3&cat=9',
  'http://rss.bt-chat.com/?group=4'
  ) 

RSSDOWNLOAD = {
  'http://www.ebookshare.net/plus/rss/index.xml': ['http://(.+?)/.+-(\d+)\.html','http://\g<1>/download.php?id=\g<2>']
  }

DEBUG=1

def dprint(debugstr):
  if DEBUG == 1:
	print debugstr

def http_conn(url):

  if 'http://' in url:
	url = url.replace('http://','',1)

  url = url.partition('/')

  dprint('[+] connecting to '+url[0]+'/'+url[2])
  http_connection = httplib.HTTPConnection(url[0])
  http_connection.request('GET',"/"+url[2])
  http_response = http_connection.getresponse();

  dprint('[+] response for '+url[0]+'/'+url[2]+' is "'+str(http_response.status)+' '+http_response.reason+'"'+http_response.getheader('Content-Type'))

# Content-Disposition=attachment; filename="Active.Directory.Objects.in.Windows.Server.2008-LiB.torrent"

  if 'x-bittorrent' in http_response.getheader('Content-Type'):
	dprint('[+] downloading torrent '+url[0]+'/'+url[2])


def readfeed(url):
  dprint('[+] connecting to RSS feed '+url)

  rssfeed = feedparser.parse(url)

  for rssentry in rssfeed.entries:
	dprint('[+] torrent title - "'+rssentry.title+'"')
	link = rssentry.link

	if url in RSSDOWNLOAD:
	  dprint('[+] feed in the RSSDOWNLOAD list, org link '+rssentry.link)
	  rssentry.link = re.sub(RSSDOWNLOAD[url][0],RSSDOWNLOAD[url][1],rssentry.link)
	  dprint('[+] new link :'+rssentry.link)

	http_conn(rssentry.link)


if __name__ == '__main__':

  for feed in RSSFEEDS:
	readfeed(feed)
