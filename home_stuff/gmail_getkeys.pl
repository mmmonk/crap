#!/usr/bin/perl

# $Id$

use strict;
use warnings;

my $file=shift;

my %emails=();

open(FD,$file);
while(<FD>){
	$_=lc;
	s/(\"|\r|\n)//g;
	s/(e-mail address: |im: .+?: )//g;

	my @a = split (',',$_);
	foreach my $f (@a){
		$emails{$f}=1 if ($f=~/\@/);
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
