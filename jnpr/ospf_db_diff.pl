#!/usr/bin/perl -w

# $Id$

use strict;
use warnings;

my %td;

my $difftime=60;

my $firstfile=1;

opendir(DIR,".");
my @files=readdir(DIR);

foreach my $file (sort @files){
	next unless ($file=~/^\d\d_getospfdb/);
	open(FD,$file);

	my %td1;

	while(<FD>){
		next unless (/^\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+)\s+0x/);

		next if ($1 eq $2);

		if (exists($td{"$1 $2"})){
			my $diff=$3-$td{"$1 $2"};
			
			if ($diff < $difftime or $diff > $difftime+5){
				print "$file: $1 $2 $diff ($3-".$td{"$1 $2"}.")\n";
			}
			$td1{"$1 $2"}=$3;
		}else{

			print "$file: add $1 $2\n" unless ($firstfile==1);
			$td1{"$1 $2"}=$3;
		}
	}
	close(FD);

	foreach my $route (keys %td){
		print "$file: rem $route\n" unless (exists($td1{$route}));
	}

	$firstfile=0;
	%td=%td1;
}
closedir(DIR);

