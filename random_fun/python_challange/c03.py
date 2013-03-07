#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/def/equality.html

import urllib
import sys
import re

t = urllib.URLopener().open("http://www.pythonchallenge.com/pc/def/equality.html").read()
a = re.search("<!--(.+)-->",t,re.S).group(1)
b = re.findall("[^A-Z][A-Z]{3}([a-z])[A-Z]{3}[^A-Z]",a)

print "".join(b)
