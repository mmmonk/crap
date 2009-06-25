#!/usr/bin/perl

use strict;
use warnings;

my $file=shift;

my %emails=();

open(FD,$file);
while(<FD>){
	chomp;
	$_=lc;
	s/\".+?\"//;
	my @a=split(',',$_);
	if ($a[0]=~/@/){
		$emails{$a[0]}=1;
	}else{
		$emails{$a[1]}=1;
	}
}
close(FD);

foreach my $e (sort keys %emails){
	next unless $e;
	next if ($e=~/prod.writely.com/);
	open(GPG,"gpg --batch --search $e | grep -i key |");
	my @keys=<GPG>;
	close(GPG);
	if ($keys[0]){
		my $key=$keys[0];
		chomp $key;
		$key=~s/.*?key (.+?),.*/$1/;
		`gpg --batch --recv-keys $key`;
	}
	sleep 5;
}
