#!/usr/bin/perl

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2007, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use warnings;
use strict;
use IO::Socket;

my $pserver = shift @ARGV;
my $pport = shift @ARGV;
my $host = shift @ARGV;
my $port = shift @ARGV;

die "Usage: $0 proxyipaddres proxyport host port\n" unless $port and not @ARGV;

my $sock = IO::Socket::INET->new(
	Proto => "tcp",
	PeerAddr => $pserver,
	PeerPort => $pport,
) or die "cannot connect to $pserver\n";

if ( fork ) {
	my $data;
	while ( 1 ) {
		my $bytes_read = sysread $sock, $data, 1500;
		if ( not $bytes_read ) {
			warn "No more data from ssh server - exiting.\n";
			exit 0;
		}
		syswrite STDOUT, $data, $bytes_read;
	}
} else {
	my $cmd="connect $host:$port HTTP/1.0\nHOST $host:$port\n\n";
#	my $cmd="testssh\n";
	syswrite $sock, $cmd, length($cmd);
	while ( 1 ) {
		my $data;
		my $bl = sysread STDIN, $data, 1400;
		if ( not $bl) {
			$sock->shutdown('SHUT_RDWR');
			exit 0;
		}
		syswrite $sock, $data, $bl;
	}
}
