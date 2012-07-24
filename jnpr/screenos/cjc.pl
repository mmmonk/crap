#!/usr/bin/perl

# $Id: 20120722$
# $Date: 2012-07-22 17:37:43$
# $Author: Marek Lukaszuk$

# clearing a bit the output of "get tech"

use strict;
use warnings;
use integer;

my $empty = 0;

while(<>){
  if (/^\s*$/){
    $empty++;
  }else{
    $empty = 0;
  }
  next if ($empty > 1);
  s/(\x07)+/\n/g;
  s/--- more ---              //;
  s/---\(more\)---(\x0d\s+\x0d)?//;
  s/---\(more \d+%\)---(\x0d\s+\x0d)?//;
  s/(\x08|\x0d)//g;
  s/---\(more\)---(\ ){39}//;
  print;
}

