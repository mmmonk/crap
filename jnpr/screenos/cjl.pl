#!/usr/bin/perl

# $Id$

# mlukaszuk@juniper.net
# clearing a bit the output of "get event"
#

use strict;
use warnings;
use integer;

while(<>){
	s/(\x08|\x0d)//g;
	s/^--- more ---              //;
	s/\s+/ /g;
	s/\s+$//;
	s/^20/\n20/;
	s/^Total/\nTotal/;
	print;
}

