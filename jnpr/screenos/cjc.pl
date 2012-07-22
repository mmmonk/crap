#!/usr/bin/perl

# $Id: 20120722$
# $Date: 2012-07-22 15:09:34$
# $Author: Marek Lukaszuk$

# clearing a bit the output of "get tech"

use strict;
use warnings;
use integer;

while(<>){
  next if /^\s*$/;
  s/--- more ---              //;
  s/---\(more\)---(\x0d\s+\x0d)?//;
  s/---\(more \d+%\)---(\x0d\s+\x0d)?//;
  s/(\x08|\x0d)//g;
  s/---\(more\)---(\ ){39}//;
  print;
}

