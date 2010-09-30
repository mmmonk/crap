#!/usr/bin/perl

use strict;
use warnings;
use integer;

my $file=shift;
open(FD,$file) or die "can't open file: $!\n";

my $indevobj=0;
my $inmgt=0;
my $pre=0;
my $first=0;

while (<FD>){
	$indevobj=1 if (/^deviceobj/);
	if ($indevobj==1){
		if (/^\s+\)\s*$/ and $inmgt==1){
			$inmgt=0;	
		}
		$inmgt=1 if (/^\s+:(\d+)?\s+\(mgt\s*$/i);
		if ($inmgt==1){
			if (/^(\s+):block\s*\(true\)\s*$/){
				print "$1:predefined-zone (true)\n";
				s/true/false/i;
			}
			if (/:predefined-zone/){
				next;
			}
		}
	  $indevobj=0 if (/^END/);
	}
	print;
}

close(FD)

