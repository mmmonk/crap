#!/usr/bin/perl

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2008, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use warnings;
use strict;

use Digest::SHA qw(sha512);
use IO::Socket::INET;
use threads('stack_size' => 16384,'exit' => 'threads_only');

my $port = shift @ARGV;

my $secret="I67Fkjpjgi5rWymauvkRBUqAAKhprAG57tU4Ke5j6ZV2KnUk0S0tQQXAnkxOAtPASqfmPGMb4ShpgHefSZM8dIucgJ52RCEaJUAWzm0gEW7YJbrkBb489EpiZnh0hZ7S";


die "Usage: $0 port\n" unless $port and not @ARGV;

sub io_rt;
sub io_wt;

my $ssh_srv = IO::Socket::INET->new(
	Listen => 5,
	Proto => "tcp",
	LocalPort => "$port",
	ReuseAddr => 1
) or warn "cannot bind to port $port\n";

my ($cli,$peer)=$ssh_srv->accept();
my ($pp,$ph) = sockaddr_in($peer);
warn ">>>> connection from ".(inet_ntoa($ph)).":$pp <<<<\n";

### AUTHORIZATION
my $data=sha512(rand().$$.time().$$.rand());
warn ">>>> auth send: $data <<<<\n";
syswrite $cli, $data, length($data);
$data=$data.$secret;
my $data1=sha512($data);
sysread $cli, $data, 1448;

die ">>>> AUTH WRONG <<<<\n" if ($data ne $data1);

### GIVING BANNER TO THE CLIENT
$data="SSH-2.0-OpenSSH_4.7p1 Debian-4\n";
syswrite STDOUT,$data, length($data);



my $proxyr = threads->create('io_rt',$cli);
my $proxyw = threads->create('io_wt',$cli);

$proxyr->join;
$proxyw->join;

shutdown($ssh_srv,2);

sub io_rt {
	my $read=shift;
	my $data;

	while (1) {
		my $br = sysread $read, $data, 1448;
		if ( not $br ) {
			shutdown($read,2);
			exit;
		}else{
			syswrite STDOUT, $data, $br;
		}
	}
}

sub io_wt {
	my $write=shift;
	my $data;

	while (1) {
		my $br = sysread STDIN, $data, 1448;
		if ( not $br ) {
			shutdown($write,2);
			exit;
		}else{
			syswrite $write, $data, $br;
		}
	}
}
