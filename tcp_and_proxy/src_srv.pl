#!/usr/bin/perl

# $Id$





# socat READLINE OPENSSL:www.gem24.pl:443,verify=0

use warnings;
use strict;

use POSIX;
use Digest::SHA qw(sha512_base64);
use Socket;
use threads('stack_size' => 16384,'exit' => 'threads_only');

my $host = shift @ARGV;
my $port = shift @ARGV || '443';
my $pserver = '127.0.0.1';
my $pport = 1080;
my $sver = 5;
my $ssh_server = "127.0.0.1";
my $ssh_srv_prt = 22;

my $secret="I67Fkjpjgi5rWymauvkRBUqAAKhprAG57tU4Ke5j6ZV2KnUk0S0tQQXAnkxOAtPASqfmPGMb4ShpgHefSZM8dIucgJ52RCEaJUAWzm0gEW7YJbrkBb489EpiZnh0hZ7S";

my $connect_timeout = 10;

sub io_thread;
sub ct;

warn ct,"connecting to: ".$host.":".$port." via socks proxy ".$pserver.":".$pport." every ".$connect_timeout." seconds\n";


while (1) {
	sleep $connect_timeout;

	my $socks;
	socket($socks,PF_INET,SOCK_STREAM,6);
	if (! connect($socks,sockaddr_in($pport,inet_aton($pserver)))){
		warn ct,"proxy server ".$pserver.":".$pport." not responding\n";
		next;
	}

	my $socks_conn;

	if ($sver eq 5){
		# connection using SOCKS5
		# http://tools.ietf.org/html/rfc1928

		$socks_conn = pack('ccc',5,1,0);

		syswrite $socks, $socks_conn, length($socks_conn);
		sysread $socks, $socks_conn, 1024;

		$socks_conn = (unpack('cc',$socks_conn))[1];

		if ($socks_conn eq 255){
			warn ct,"socks server says wrong authentication type\n";
			next;	
		}

		if ($host=~/^\d+\.\d+\.\d+\.\d+$/){
			$socks_conn = pack('cccc',5,1,0,1).inet_aton($host).pack('n',$port);
		}else{
			$socks_conn = pack('ccccc',5,1,0,3,length($host)).$host.pack('n',$port);
		}

	} elsif ($sver eq 4) {
		# we are connecting to IPv4 address, using SOCKS4
		if ($host=~/^\d+\.\d+\.\d+\.\d+$/){
			$socks_conn = pack('ccn',4,1,$port).inet_aton($host).chr(0);
		}else{
		# we are connecting to FQDN, using SOCKS4A
			$socks_conn = pack('ccn',4,1,$port).inet_aton('0.0.0.20').chr(0).$host.chr(0);
		}

	}else{
		die ct,"the version ".$sver." of socks protocol is not implemented\n";
	}

	syswrite $socks, $socks_conn, length($socks_conn);
	sysread $socks, $socks_conn, 256;

	$socks_conn = (unpack('cc',$socks_conn))[1];
	next unless ($socks_conn);

	if ($socks_conn ne 0){
		warn ct,"connection not allowed\n";
		next;
	}else{
		warn ct,"connected to proxy server ".$pserver.":".$pport."\n";
	}

	### AUTHORIZATION
	my $data;
  sysread $socks, $data, 86;

	unless ($data){
		warn ct,"connected to proxy server ".$pserver.":".$pport." - timeout\n";
		undef $socks;
		undef $data;
		next;
	}else{
		warn ct,"connected to proxy server ".$pserver.":".$pport." - the host ".$host.":".$port." responded\n";
	}

	$data=$data.$secret;
  $data=sha512_base64($data);

  syswrite $socks, $data, length($data);

	warn ct,"sending auth data\n";

	my $ssh;
  socket($ssh,PF_INET,SOCK_STREAM,6);
  if (! connect($ssh,sockaddr_in($ssh_srv_prt,inet_aton($ssh_server)))){
          warn ct,"ssh server at ".$ssh_server.":".$ssh_srv_prt." is not responding\n"; 
          next;
  }else{
		warn ct,"connected to SSH server at ".$ssh_server.":".$ssh_srv_prt."\n";
	}

	# REMOVING BANNER
	sysread $ssh, $data, 86;
	warn ct,"removing SSH server banner: $data\n";

	# GOOD TO GO
	my $proxyr = threads->create('io_thread',$socks,$ssh);
	my $proxyw = threads->create('io_thread',$ssh,$socks);

	$proxyr->join;
	$proxyw->join;

	undef $socks;
	undef $data;
	undef $ssh;
	undef $proxyr;
	undef $proxyw;
}

sub io_thread {
	my $read=shift;
	my $write=shift;
	my $data;

	warn ct,"starting thread\n";
	while (1) {
		my $br = sysread $read, $data, 1448;
		if ( not $br ) {
			warn ct,"exiting thread, closing connection\n";
			undef $data;
			undef $br;
			shutdown($read,2);
			shutdown($write,2);
			undef $read;
			undef $write;
			exit;
		}else{
			syswrite $write, $data, $br;
		}
	}
}

sub ct {
	$_ = asctime(localtime(time));
	chomp;
	return "$_ - "; 
}
