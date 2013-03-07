#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/def/integrity.html

import urllib, re

t = urllib.URLopener().open("http://www.pythonchallenge.com/pc/def/integrity.html").read()

a = re.search("<!--(.+)-->",t,re.S).group(1)

for l in a.split("\n"):
  if ":" in l:
    b = l.split("'")
    print str(b[0])+str(b[1].decode('string_escape').decode('bz2'))

