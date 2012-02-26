#!/usr/bin/perl -wW

use strict;

use Net::Netmask;

while (<>){
	chomp;
	if ($_=~/\d+\.\d+\.\d+\.\d+ \d+\.\d+\.\d+\.\d+/){
		my @a=split(" ",$_);
		my $n=new Net::Netmask ($a[0],$a[1]);

		print "".$n->base()."/".$n->bits()."\n";
	}else{
		if ($_=~/\d+\.\d+\.\d+\.\d+\/\d+/){
			my $n=new Net::Netmask ($_);
			print "".$n->base()."/".$n->mask()."\n";
		}
	}
}
