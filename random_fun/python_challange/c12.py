#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/return/evil.html
# http://www.pythonchallenge.com/pc/return/evil1.jpg
# http://www.pythonchallenge.com/pc/return/evil2.jpg
# http://www.pythonchallenge.com/pc/return/evil3.jpg
# http://www.pythonchallenge.com/pc/return/evil4.jpg
# http://www.pythonchallenge.com/pc/return/bert.html

import urllib2

auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password(realm='inflate', uri='http://www.pythonchallenge.com/pc/return/', user='huge', passwd='file')
opener = urllib2.build_opener(auth_handler)
urllib2.install_opener(opener)

pic = urllib2.urlopen('http://www.pythonchallenge.com/pc/return/evil2.gfx').read()

for j in xrange(0,5):
  pic2 = ""
  i = j
  while True:
    pic2 += pic[i]
    i += 5
    if i >= len(pic):
      break

  open("evil2-"+str(j)+".bin","wb").write(pic2)
