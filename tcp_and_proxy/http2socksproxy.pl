#!/usr/bin/perl

### Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
### Copyright (c) 2008, Marek £ukaszuk 
### BSD License at http://monkey.geeks.pl/bsd/

### http://en.wikipedia.org/wiki/SOCKS

use warnings;
use strict;
use Socket;
use threads('stack_size' => 16384,'exit' => 'threads_only');

my $pserver = "127.0.0.1";
my $pport = "1081";
my $host = shift @ARGV;
my $port = shift @ARGV;
my $sver = shift @ARGV;

$sver = 5 unless $sver;

#die "Usage: $0 proxyipaddres proxyport host port\n" unless $port and not @ARGV;

###
### sub for the read thread
###
sub proxy {
	my $sockr=shift;
	my $sockw=shift;
	my $scanCG=shift;
	my $data;

	while ( 1 ) {
		my $bytes_read = sysread $sockr, $data, 1500;
		if ( not $bytes_read ) {
			shutdown($sockr,2);
			shutdown($sockw,2);
			exit;
		}
		syswrite $sockw, $data, $bytes_read;
	}
}


#GET http://wp.pl/ HTTP/1.1
#CONNECT mail.google.com:443 HTTP/1.1

my $LISTEN;
my $CONN;
socket ($LISTEN, PF_INET, SOCK_STREAM, 6);
setsockopt ($LISTEN, SOL_SOCKET, SO_REUSEADDR, 1);
bind ($LISTEN, sockaddr_in(8081,inet_aton("127.0.0.1")));
listen ($LISTEN, 50);
while ( accept($CONN, $LISTEN) ){
	my $t_client=threads->create('takecall',$CONN);
	$t_client->join;	
}

sub takecall{
	my $CLI_CONN=shift;

	my $data;
	my $bl = sysread $CLI_CONN, $data, 1450;
	my $host=$data;
	if ($host=~/(^GET|^POST) /){
		$host=~s/(GET|POST) .+tp:\/\/(.+?)( |\/).*/$2/s;
	}elsif($host=~/^CONNECT /){
		$host=~s/CONNECT (.+?) .*/$1/s;
	}else{
		print "ERROR: $host\n";
		close($CLI_CONN);
	}

	my @h=split(':',$host);

	unless (defined($h[1])){ $h[1]=80; }
	pconnect($CONN,$h[0],$h[1],5,$data);
	shutdown($CONN,2);
	exit;
}


sub pconnect{
	my $CLI_CONN=shift;
	my $host = shift;
	my $port = shift;
	my $sver = shift;
	my $data = shift;

	my $SOCKS;
	socket($SOCKS,PF_INET,SOCK_STREAM,6);
	connect($SOCKS,sockaddr_in($pport,inet_aton($pserver))) or die "\n>>> proxy server ".$pserver.":".$pport." not responding <<<\n";

	my $socks_conn;

	if ($sver eq 5){
		###
		### connection using SOCKS5
		###
		### http://tools.ietf.org/html/rfc1928
		
		$socks_conn = pack('ccc',5,1,0);

		syswrite $SOCKS, $socks_conn, length($socks_conn);
		sysread $SOCKS, $socks_conn, 1024;

		$socks_conn = (unpack('cc',$socks_conn))[1];

		die "\n>>> wrong authentication type <<<\n\n" if ($socks_conn eq 255);

		if ($host=~/^\d+\.\d+\.\d+\.\d+$/){
			$socks_conn = pack('cccc',5,1,0,1).inet_aton($host).pack('n',$port);
		}else{
			$socks_conn = pack('ccccc',5,1,0,3,length($host)).$host.pack('n',$port);
		}

		syswrite $SOCKS, $socks_conn, length($socks_conn);
		sysread $SOCKS, $socks_conn, 1024;

		$socks_conn = (unpack('cc',$socks_conn))[1];

		die "\n>>> connection not allowed <<<\n\n" unless ($socks_conn eq 0);

	} elsif ($sver eq 4) {

		####
		#### we are connecting to IPv4 address, using SOCKS4
		####
		if ($host=~/^\d+\.\d+\.\d+\.\d+$/){
			$socks_conn = pack('ccn',4,1,$port).inet_aton($host).chr(0);
		}else{
		####
		#### we are connecting to FQDN, using SOCKS4A
		####
			$socks_conn = pack('ccn',4,1,$port).inet_aton('0.0.0.20').chr(0).$host.chr(0);
		}
		
		syswrite $SOCKS, $socks_conn, length($socks_conn);
		sysread $SOCKS, $socks_conn, 8;

		$socks_conn = (unpack('cc',$socks_conn))[1];

		die "\n>>> connection not allowed <<<\n\n" unless ($socks_conn eq 90);

	}else{
		die "\n>>> not implemented <<<\n\n";
	}

	syswrite($SOCKS,$data,length($data));

	my $proxyr = threads->create('proxy',$SOCKS,$CLI_CONN);
	my $proxyw = threads->create('proxy',$CLI_CONN,$SOCKS);

	$proxyw->join;
	$proxyr->join;
	
	shutdown($SOCKS,2);
}
