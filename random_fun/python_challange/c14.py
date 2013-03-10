#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/return/italy.html
# <!-- remember: 100*100 = (100+99+99+98) + (...  -->

import Image
import urllib2
import StringIO

auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password(realm='inflate', uri='http://www.pythonchallenge.com/pc/return/', user='huge', passwd='file')
opener = urllib2.build_opener(auth_handler)
urllib2.install_opener(opener)

pic = urllib2.urlopen('http://www.pythonchallenge.com/pc/return/wire.png').read()
img = Image.open(StringIO.StringIO(pic))

nimg = list() #Image.new('RGB',(200,1))

c = 100
s = 0
i = 0

s += c
nimg.append(img.getpixel((s-1,0)))
c -= 1
i += 1
while True:
  s += c
  s += c
  nimg.append(img.getpixel((s-1,0)))
  i += 1
  c -= 1
  if i == 199:
    break

nimg.append(img.getpixel((s-1,0)))

nimg = [ str(x) for x in nimg ]

print "\n".join(nimg)
