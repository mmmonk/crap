#!/usr/bin/perl -w

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2005, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use strict;
use integer;

use Net::SNMP;

my $cpu5minold  =	'1.3.6.1.4.1.9.2.1.58.0';
my $cpu5min =		'1.3.6.1.4.1.9.9.109.1.1.1.1.8.1';
my $readcom =		'public';
my $query = 		shift;

my $yellow = 		65;
my $red =		85;

my ($session, $error) = Net::SNMP->session(
        -timeout        => 3,
        -retries        => 5,
        -hostname       => $query,
        -community      => $readcom,
        -port           => 161,
        -version        => 2,
        -translate      => 0
);
if (!defined($session)){
	$session->close;
	exit;
}

my $re=$session->get_request( -varbindlist => [ $cpu5minold,$cpu5min ]);
exit if (!$re);

my $load=$re->{$cpu5min};
my $loadold=$re->{$cpu5minold};

$session->close;

unless ($load){
	$load=$loadold;
}

print "CPU:$load%";

my $exit=0;
if ($load>$yellow){
	$exit=1;
	if ($load>$red){
		$exit=2;
	}
}

exit $exit;
