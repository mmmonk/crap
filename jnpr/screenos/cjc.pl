#!/usr/bin/perl

# $Id$

# mlukaszuk@juniper.net
# clearing a bit the output of "get tech"
# 

use strict;
use warnings;
use integer;

while(<>){
  s/(\x08|\x0d)//g;
  s/--- more ---              //;
  s/---\(more\)---\x0d\s+\x0d//;
  s/---\(more \d+%\)---\x0d\s+\x0d//;
  s/(\x08|\x0d)//g;
  s/---\(more\)---(\ ){39}//;
  print;
}

