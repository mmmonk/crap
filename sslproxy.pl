#!/usr/bin/perl

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2007, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

#use warnings;
use strict;
use Socket;
use Net::SSLeay;
Net::SSLeay::SSLeay_add_ssl_algorithms();
Net::SSLeay::randomize();

my $pserver = shift @ARGV;
my $pport = shift @ARGV;
my $host = shift @ARGV;
my $port = shift @ARGV;

die "Usage: $0 proxyipaddres proxyport host port\n" unless $port and not @ARGV;

my $sin = sockaddr_in ($pport,inet_aton($pserver));
socket(proxy,&AF_INET,&SOCK_STREAM,getprotobyname('tcp')) or die "socket: $!";
connect(proxy,$sin) or die "connect: $!";

#my $cmd="connect $host:$port HTTP/1.0\nHOST $host:$port\n\n";
#syswrite proxy, $cmd, length($cmd);

my $ctx = Net::SSLeay::CTX_v23_new () or die ("CTX_new: $!");
my $ssl = Net::SSLeay::new($ctx) or die ("client: SSL_new: $!");
Net::SSLeay::set_fd($ssl, fileno(proxy));
Net::SSLeay::set_mode($ssl,'SSL_MODE_AUTO_RETRY');
my $cipher_list='DH-RSA-AES256-SHA:AES256-SHA:AES';
Net::SSLeay::set_cipher_list($ssl,$cipher_list);
Net::SSLeay::connect($ssl);
warn "client: Cipher '" . Net::SSLeay::get_cipher($ssl) . "'\n";
warn "cert: ".Net::SSLeay::dump_peer_certificate($ssl)."\n";

my $rekey_limit=10240;
my $rekey_r=0;
my $rekey_w=0;

if ( fork ) {
	my $data;
	while ( 1 ) {
		$data = Net::SSLeay::read($ssl);
		if ($rekey_r > $rekey_limit){
#			warn "rekey limit read reached\n";
			$rekey_r=0;
		}
		if ( ! $data ) {
			warn "No more data from ssh server - exiting.\n";
			exit 0;
		}
		$rekey_r+=length($data);
		syswrite STDOUT, $data, length($data);
	}
} else {
#	my $cmd="connect $host:$port HTTP/1.0\nHOST $host:$port\n\n";
	my $cmd="testssh\n";
	Net::SSLeay::write($ssl, $cmd);
	while ( 1 ) {
		my $data;
		my $bl = sysread STDIN, $data, 1400;
		$rekey_w+=$bl;
		if ($rekey_w > $rekey_limit){
#			warn "rekey limit write reached\n";
			$rekey_w=0;
		}
		if ( not $bl) {
			shutdown(proxy,&SHUT_RDWR);
			exit 0;
		}
		Net::SSLeay::write($ssl, $data);
	}
}

