#!/usr/bin/perl -wW

use strict;

use Net::Netmask;

while (<>){
	chomp;
	my $n=new Net::Netmask ($_);
	print "".$n->base()."/".$n->bits()."\n";
}
