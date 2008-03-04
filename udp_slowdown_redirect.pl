#!/usr/bin/perl

use strict;
use warnings;
use IO::Socket;
use POSIX;

my $lport=shift;
my $dport=shift;
my $delay=shift;
my $MAX_TO_READ=1000;
my $data;

my $srv = IO::Socket::INET->new(Proto => "udp", LocalPort => $lport)
    or die "Couldn't be a udp server on port $lport : $!\n";

my $cli = IO::Socket::INET->new(Proto => "udp", PeerPort => $dport, PeerAddr => "127.0.0.1") or die "Couldn't create socket: $!\n";

while ($srv->recv($data, $MAX_TO_READ)) {
	print "######### new request ############\n";
	print ">> ".time." got something sending it the server\n";
	$cli->send($data);
	print "<  ".time." got answer\n";
	$cli->recv($data,$MAX_TO_READ);
	print "?? ".time." sleeping for $delay seconds\n";
	select(undef, undef, undef, $delay);
	print ">  ".time." sending to the client\n";
	$srv->send($data);
} 
