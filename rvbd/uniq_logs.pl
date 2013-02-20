#!/usr/bin/perl

# $Id: 20130220$
# $Date: 2013-02-20 15:56:03$
# $Author: Marek Lukaszuk$

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
