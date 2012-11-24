#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/return/good.html

import Image, ImageDraw, urllib2, StringIO, re

auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password(realm='inflate', uri='http://www.pythonchallenge.com/pc/return/', user='huge', passwd='file')
opener = urllib2.build_opener(auth_handler)
urllib2.install_opener(opener)
pic = urllib2.urlopen('http://www.pythonchallenge.com/pc/return/good.jpg').read()

html = urllib2.urlopen('http://www.pythonchallenge.com/pc/return/good.html').read()

f = [int(i) for i in re.search("first:(.+?)\n\n",html,re.S).group(1).replace("\n","").split(",")]
s = [int(i) for i in re.search("second:(.+?)\n\n",html,re.S).group(1).replace("\n","").split(",")]

img = Image.open(StringIO.StringIO(pic))

c = (255,0,0)
draw = ImageDraw.Draw(img)
draw.polygon(f,outline=c)
draw.polygon(s,outline=c)

img.show()
