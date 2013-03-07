#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/def/oxygen.html

import urllib
import Image
import StringIO

png = urllib.URLopener().open("http://www.pythonchallenge.com/pc/def/oxygen.png").read()

img = Image.open(StringIO.StringIO(png))

bbox = img.getbbox()

for y in xrange(0,bbox[3]):
  p = img.getpixel((0,y))

  if p[0] == p[1] and p[0] == p[2]:
    m = ""
    for x in xrange(0,bbox[2]/7):
      px = img.getpixel((x*7,y))
      if px[0] == px[1] and px[0] == px[2]:
        m += chr(px[0])
      else:
        break
    print m
    break

o = m[m.index('[')+1:m.index(']')]
print o+" =",
print "".join([ chr(int(c)) for c in o.split(',')])
