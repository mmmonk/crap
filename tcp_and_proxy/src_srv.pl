#!/usr/bin/perl

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2008, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use warnings;
use strict;

use POSIX;
use Digest::SHA qw(sha512_base64);
use IO::Socket::Socks;
use IO::Socket::INET;
use threads('stack_size' => 16384,'exit' => 'threads_only');

my $DEBUG=0;

my $pserver = shift @ARGV;
my $pport = shift @ARGV;
my $host = shift @ARGV;
my $port = shift @ARGV;

my $secret="I67Fkjpjgi5rWymauvkRBUqAAKhprAG57tU4Ke5j6ZV2KnUk0S0tQQXAnkxOAtPASqfmPGMb4ShpgHefSZM8dIucgJ52RCEaJUAWzm0gEW7YJbrkBb489EpiZnh0hZ7S";

die "Usage: $0 proxyipaddres proxyport host port\n" unless $port and not @ARGV;

sub io_thread;
sub ct;


while (1) {
	sleep 10;

	my $sock = new IO::Socket::Socks(ProxyAddr  => $pserver,
					ProxyPort   => $pport,
					ConnectAddr => $host,
					ConnectPort => $port);

	unless ($sock){
		warn ct," - proxy server ".$pserver.":".$pport." not responding\n";
		next;
	}	

	warn ct," - connected to proxy server ".$pserver.":".$pport."\n";

	### AUTHORIZATION
	my $data;
        sysread $sock, $data, 86;
	warn ">>> auth recv: $data <<<<\n" if ($DEBUG==1); 
	$data=$data.$secret;
        $data=sha512_base64($data);
	warn ">>> auth send: $data <<<<\n" if ($DEBUG==1);
        syswrite $sock, $data, length($data);

	my $ssh = IO::Socket::INET->new(
		Proto => "tcp",
		PeerAddr => "127.0.0.1",
		PeerPort => "22"
	) or warn "cannot connect to $host:$port\n";

	unless ($ssh){
		warn "cannot connect to ".$host.":".$port."\n";
		next;
	}

	### REMOVING BANNER
	sysread $ssh, $data, 86;

	### GOOD TO GO	
	my $proxyr = threads->create('io_thread',$sock,$ssh);
	my $proxyw = threads->create('io_thread',$ssh,$sock);

	$proxyr->join;
	$proxyw->join;
}

sub io_thread {
	my $read=shift;
	my $write=shift;
	my $data;

	while (1) {
		my $br = sysread $read, $data, 1448;
		if ( not $br ) {
			shutdown($read,2);
			shutdown($write,2);
			exit;
		}else{
			syswrite $write, $data, $br;
		}
	}
}

sub ct {
	$_=asctime(localtime(time));
	chomp;
	return $_; 
}
