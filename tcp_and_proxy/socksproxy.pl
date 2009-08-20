#!/usr/bin/perl

### Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
### Copyright (c) 2009, Marek £ukaszuk 
### BSD License at http://monkey.geeks.pl/bsd/

### http://en.wikipedia.org/wiki/SOCKS

use warnings;
use strict;
use Socket;
use threads('stack_size' => 16384);

my $pserver = shift @ARGV;
my $pport = shift @ARGV;
my $host = shift @ARGV;
my $port = shift @ARGV;
my $sver = shift @ARGV;

$sver = 5 unless $sver;

die "Usage: $0 proxyipaddres proxyport host port\n" unless $port and not @ARGV;

sub proxyread; 
sub proxywrite;

my $SOCKS;
socket($SOCKS,PF_INET,SOCK_STREAM,6);
connect($SOCKS,sockaddr_in($pport,inet_aton($pserver))) or die "\n>>> proxy server ".$pserver.":".$pport." not responding <<<\n";

my $socks_conn;

if ($sver eq 5){
	### connection using SOCKS5
	### http://tools.ietf.org/html/rfc1928
	$socks_conn = pack('ccc',5,1,0);
	syswrite $SOCKS, $socks_conn, length($socks_conn);
	sysread $SOCKS, $socks_conn, 1024;
	$socks_conn = (unpack('cc',$socks_conn))[1];
	die "\n>>> wrong authentication tyoe <<<\n\n" if ($socks_conn eq 255);
	if ($host=~/^\d+\.\d+\.\d+\.\d+$/){
		$socks_conn = pack('cccc',5,1,0,1).inet_aton($host).pack('n',$port);
	}else{
		$socks_conn = pack('ccccc',5,1,0,3,length($host)).$host.pack('n',$port);
	}
} elsif ($sver eq 4) {
	#### we are connecting to IPv4 address, using SOCKS4
	if ($host=~/^\d+\.\d+\.\d+\.\d+$/){
		$socks_conn = pack('ccn',4,1,$port).inet_aton($host).chr(0);
	}else{
	#### we are connecting to FQDN, using SOCKS4A
		$socks_conn = pack('ccn',4,1,$port).inet_aton('0.0.0.20').chr(0).$host.chr(0);
	}
}else{
	die "\n>>> version $sver not implemented <<<\n\n";
}

syswrite $SOCKS, $socks_conn, length($socks_conn);
sysread $SOCKS, $socks_conn, 256;

die "\n>>> connection not allowed <<<\n\n" unless ((unpack('cc',$socks_conn))[1] eq 0);

my $proxyr = threads->create('proxyread',$SOCKS);
my $proxyw = threads->create('proxywrite',$SOCKS);

$proxyw->join;
$proxyr->join;



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
