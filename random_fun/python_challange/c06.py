#!/usr/bin/env python

# http://www.pythonchallenge.com/pc/def/channel.html
# http://www.pythonchallenge.com/pc/def/zip.html ;)

import urllib
import zipfile
import os

s = "90052"
tf = "temp6.zip"

open(tf,"wb").write(urllib.URLopener().open("http://www.pythonchallenge.com/pc/def/channel.zip").read())
z = zipfile.ZipFile(open(tf),mode="r")
m = ""

while True:
  try:
    t = z.open(s+".txt").read()
    m += z.getinfo(s+".txt").comment
    s = t.split()[-1]
    p = False
    print t
  except:
    print m
    os.unlink(tf)
    break

