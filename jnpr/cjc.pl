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
	print;
}

