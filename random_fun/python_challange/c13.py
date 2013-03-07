#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/return/disproportional.html
# http://www.pythonchallenge.com/pc/phonebook.php

import Image, urllib2, StringIO

auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password(realm='inflate', uri='http://www.pythonchallenge.com/pc/return/', user='huge', passwd='file')
opener = urllib2.build_opener(auth_handler)
urllib2.install_opener(opener)

pic = urllib2.urlopen('http://www.pythonchallenge.com/pc/return/evil2.gfx').read()

