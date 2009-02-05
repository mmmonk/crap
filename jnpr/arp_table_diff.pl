#!/usr/bin/perl 

use strict;
use warnings;

my %td;
my %in;

my $difftime = 60;

my $firstfile=1;

opendir(DIR,".");
my @files=readdir(DIR);

foreach my $file (sort @files){
	next unless ($file=~/^\d\d_getarp/);
	open(FD,$file);

	my %td1;

	while(<FD>){
		next unless (/^\s+(\d+\.\d+\.\d+\.\d+)\s+(.{12})\s+(.+?)\s+VLD\s+(\d+)\s+/);

		if (exists($in{"$1"})){
			unless ($in{"$1"} eq "$2 $3"){
				print "$file: mac change: $1 ".$in{$1}." -> $2 $3 : $4\n";
			}
			$in{"$1"}="$2 $3";
		}else{
			$in{"$1"}="$2 $3";
		}

		if (exists($td{"$1"})){
			my $diff=$td{"$1"}-$4;
			
			if ($diff < $difftime or $diff > $difftime+5 ){
				print "$file: $1 $2 $diff\n";
			}
			$td1{"$1"}=$4;
		}else{
			print "$file: new device $1 $2 $3\n" unless ($firstfile==1);
			$td1{"$1"}=$4;
		}
	}
	$firstfile=0;
	close(FD);
	%td=%td1;
}
closedir(DIR);

