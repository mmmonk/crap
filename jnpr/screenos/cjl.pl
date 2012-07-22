#!/usr/bin/perl

# $Id: 20120722$
# $Date: 2012-07-22 13:43:44$
# $Author: Marek Lukaszuk$

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

