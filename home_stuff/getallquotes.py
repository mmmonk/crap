#!/usr/bin/env python

import urllib2
import re

for page in xrange(1,518):
  dat = urllib2.urlopen("http://www.values.com/inspirational-quotes?page="+str(page))
  text = dat.read()
  quotes = re.findall("<span class='quotation'>&ldquo;(.+?)&rdquo;",text)
  authors = re.findall("<a href=\"/inspirational-quote-authors.+?\">(.+?)<",text)
  authors.reverse()

  for quote in quotes:
    author = authors.pop()
    while "quotes by this author" in author:
      author = authors.pop()
    print "\""+str(quote)+"\"\n  ~"+str(author)+"\n%"


