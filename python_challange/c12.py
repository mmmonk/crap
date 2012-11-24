#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/return/evil.html
# http://www.pythonchallenge.com/pc/return/bert.html

import Image, urllib2, StringIO

auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password(realm='inflate', uri='http://www.pythonchallenge.com/pc/return/', user='huge', passwd='file')
opener = urllib2.build_opener(auth_handler)
urllib2.install_opener(opener)

print urllib2.urlopen('http://www.pythonchallenge.com/pc/return/evil.html').read()

pic = urllib2.urlopen('http://www.pythonchallenge.com/pc/return/evil1.jpg').read()
e1 = Image.open(StringIO.StringIO(pic))
#e1.show()

pic = urllib2.urlopen('http://www.pythonchallenge.com/pc/return/evil2.jpg').read()
e2 = Image.open(StringIO.StringIO(pic))
#e2.show()

pic = urllib2.urlopen('http://www.pythonchallenge.com/pc/return/evil3.jpg').read()
e3 = Image.open(StringIO.StringIO(pic))
#e3.show()

print urllib2.urlopen('http://www.pythonchallenge.com/pc/return/evil4.jpg').read()

print urllib2.urlopen('http://www.pythonchallenge.com/pc/return/bert.html').read()

bert = Image.open(StringIO.StringIO(urllib2.urlopen('http://www.pythonchallenge.com/pc/return/bert.gif').read()))

#for a in bert.getdata():
#  print a

ex = bert.getextrema()
print ex
print str(ex[1]-ex[0])

#for x in xrange(0,bert.size[0]):
#  for y in xrange(0,bert.size[1]):
#    print bert.getpixel((x,y)),
