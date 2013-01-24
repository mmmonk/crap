#!/usr/bin/env python

# $Id: 20130117$
# $Date: 2013-01-17 16:52:27$
# $Author: Marek Lukaszuk$

import pymongo
import sys
import argparse

if __name__ == '__main__':

  try:
    connection = pymongo.Connection()
  except:
    print "Problem with connecting to the mongoDB"
    sys.exit(1)
  db = connection.urls
  urls = db['urls']

  # we have lower case object in the db already
  for i in urls.find({'_id': {'$regex': sys.argv[1], '$options': 'i'}}):
      print i

