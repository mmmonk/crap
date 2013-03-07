#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/return/5808.html

import Image,ImageEnhance, urllib2, StringIO

auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password(realm='inflate', uri='http://www.pythonchallenge.com/pc/return/', user='huge', passwd='file')
opener = urllib2.build_opener(auth_handler)
urllib2.install_opener(opener)
pic = urllib2.urlopen('http://www.pythonchallenge.com/pc/return/cave.jpg').read()

img = Image.open(StringIO.StringIO(pic))
img.show()
im = ImageEnhance.Brightness(img)
im.enhance(10).show()

