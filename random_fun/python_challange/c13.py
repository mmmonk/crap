#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/return/disproportional.html
# http://www.pythonchallenge.com/pc/phonebook.php

import urllib2
import xmlrpclib

auth_handler = urllib2.HTTPBasicAuthHandler()
auth_handler.add_password(realm='inflate', uri='http://www.pythonchallenge.com/pc/return/', user='huge', passwd='file')
opener = urllib2.build_opener(auth_handler)
urllib2.install_opener(opener)

#print urllib2.urlopen('http://www.pythonchallenge.com/pc/phonebook.php').read()

xml = xmlrpclib.ServerProxy("http://www.pythonchallenge.com/pc/phonebook.php",verbose=1)
pn = xml.phone("Bert")
print pn.replace("555-","").lower()

