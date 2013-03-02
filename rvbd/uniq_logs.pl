#!/usr/bin/perl

# $Id: 20130302$
# $Date: 2013-03-02 14:33:37$
# $Author: Marek Lukaszuk$

# remove from typical linux log files dates, IPs and numbers,
# this allows to quickly do some simple statistics

use strict;
use warnings;

while(<>){
  s/^\D+\s+\d+\s+\d+:\d+:\d+\s+.+?\s+//;
  s/\.(NOTICE|WARN|ERR)/.\@LEVEL/g;
  s/(?:\d+\.){3}\d+/\@IP/g;
  s/\d+/\@NUM/g;
} continue {
  print
}
