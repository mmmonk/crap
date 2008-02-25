#!/usr/bin/perl

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2008, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use warnings;
use strict;
use Net::SOCKS;
#use Socket;
use threads('stack_size' => 16384);

my $pserver = shift @ARGV;
my $pport = shift @ARGV;
my $host = shift @ARGV;
my $port = shift @ARGV;

die "Usage: $0 proxyipaddres proxyport host port\n" unless $port and not @ARGV;

### sub for the read thread
sub proxyread {
	my $pread=shift;
	my $data;
	while ( 1 ) {
		my $bytes_read = sysread $pread, $data, 1500;
		if ( not $bytes_read ) {
			warn "\n>>> No more data from proxy server - exiting <<<\n\n";
			exit;
		}
		syswrite STDOUT, $data, $bytes_read;
	}
}

### sub for the write thread
sub proxywrite {
	my $pwrite=shift;
	my $data;
	while ( 1 ) {
		my $bl = sysread STDIN, $data, 1450;
		if ( not $bl) {
			close($pwrite);
			exit;	
		}
		syswrite $pwrite, $data, $bl;
	}
}


my $sock = new Net::SOCKS(socks_addr => "$pserver",
                socks_port => "$pport",
                protocol_version => 5);

my $proxy = $sock->connect(peer_addr => "$host", peer_port => "$port");

if ($proxy){
	my $proxyr = threads->create('proxyread',$proxy);
	my $proxyw = threads->create('proxywrite',$proxy);

	$proxyw->join;
	$proxyr->join;
}else{
	warn "\n>>> proxy server ".$pserver.":".$pport." not responding <<<\n\n";
} 
