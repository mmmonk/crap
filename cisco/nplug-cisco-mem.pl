#!/usr/bin/perl

# $Id$





use strict;

use Net::SNMP;

my $mem5minused = 	'1.3.6.1.4.1.9.9.48.1.1.1.5.1';
my $mem5minfree = 	'1.3.6.1.4.1.9.9.48.1.1.1.6.1';
my $readcom =		'public';
my $query = 		shift;

my $yellow = 		65;
my $red =		90;

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

my $re=$session->get_request( -varbindlist => [ $mem5minused,$mem5minfree ]);
exit if (!$re);

my $used=$re->{$mem5minused};
my $free=$re->{$mem5minfree};
my $all=$free+$used;

$session->close;

my $pfree=int(($free/$all)*100);
my $pused=int(($used/$all)*100);

print "MEM: U:$pused F:$pfree";

my $exit=0;
if ($pused>$yellow){
	$exit=1;
	if ($pused>$red){
		$exit=2;
	}
}

exit $exit;
