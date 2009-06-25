#!/usr/bin/perl

use strict;
use warnings;

use DateTime;
use Astro::Sunrise;

my $dt=DateTime->now;

for (0..366){
	my @date=split('-',$dt->ymd);
	my ($sr,$ss) = sunrise(@date,4.77,52.27,1,undef,-6,1);
	print $dt->ymd," sr: $sr ss: $ss\n";
	$dt->add(days=>1);
}

