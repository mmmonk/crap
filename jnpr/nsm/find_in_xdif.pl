#!/usr/bin/perl

use strict;
use warnings;
use integer;

my $file=shift;
open(FD,$file) or die "can't open file: $!\n";

my $query=shift;

my $lvl1=0;
my $lvl0=0;
my $lvl2=0;
my $lvl3=0;
my $dev;
my $didit="";

while (<FD>){
	$lvl0=1 if (/^deviceobj/);
	if ($lvl0==1){
		if (/^\)/){
			$lvl1=0;
			$lvl2=0;
			$lvl3=0;
		}
		if (/^\s+:\d+\s+\((\S+)\s*$/i){;
			$dev=$1;
			$lvl1=1;
		}		
		if ($lvl1==1){
			#$lvl2=0 if (/^\s+:.+?\s*\(\s*$/ and $lvl2==1);
			if (/^\s+:type \(template\)\s*$/){
				$lvl2=1;
				$didit=$dev;
			}
			if ($lvl2==1){
				$lvl3=0 if (/^\s+:.+?\s*\(\s*$/ and $lvl3==1);
				if (/$query/){
					$lvl3=1;
				}
				if ($lvl3==1){
					if ($didit ne "") { 
						print "=>>> $didit <<<=\n";
						$didit="";
					}
					print;
				}
			}
		}
		$lvl0=0 if (/^END/);
	}
}
close(FD)

