#!/usr/bin/perl

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2008, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use warnings;
use strict;
use Socket;
use threads('stack_size' => 16384);

my $SOCKS;

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


socket($SOCKS,PF_INET,SOCK_STREAM,6);
my $sin = sockaddr_in($pport,inet_aton($pserver));
connect($SOCKS,$sin);

my $socks_conn=pack('ccn',4,1,$port).inet_aton($host).chr(0);
syswrite $SOCKS, $socks_conn, length($socks_conn);
sysread $SOCKS, $socks_conn, 8;
$socks_conn=(unpack('cc',$socks_conn))[1];

if ($socks_conn eq 90){
	my $proxyr = threads->create('proxyread',$SOCKS);
	my $proxyw = threads->create('proxywrite',$SOCKS);

	$proxyw->join;
	$proxyr->join;
}else{
	warn "\n>>> proxy server ".$pserver.":".$pport." not responding <<<\n\n";
}

