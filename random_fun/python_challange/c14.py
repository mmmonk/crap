#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/return/italy.html

import Image, urllib2
import StringIO

auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password(realm='inflate', uri='http://www.pythonchallenge.com/pc/return/', user='huge', passwd='file')
opener = urllib2.build_opener(auth_handler)
urllib2.install_opener(opener)

pic = urllib2.urlopen('http://www.pythonchallenge.com/pc/return/wire.png').read()
img = Image.open(StringIO.StringIO(pic))

nimg = Image.new('RGB',(200,1))

c = 100
s = 0
i = 0

s += c
nimg.putpixel((i,0),img.getpixel((s-1,0)))
while True:
  i += 1
  s += (c-1)
  nimg.putpixel((i,0),img.getpixel((s-1,0)))
  i += 1
  s += (c-1)
  #nimg.putpixel((i,0),img.getpixel((s-1,0)))
  i += 1
  s += (c-2)
  nimg.putpixel((i,0),img.getpixel((s-1,0)))
  i += 1
  c -= 2
  if i == 200:
    break
  print str(i)+" "+str(s)

fd = open("wire.png","wb")
nimg.save(fd)
fd.close()
