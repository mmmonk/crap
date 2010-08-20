#!/usr/bin/perl

# $Id$





use warnings;
use strict;

use Digest::SHA qw(sha512_base64);
use IO::Socket::INET;
use threads('stack_size' => 16384,'exit' => 'threads_only');

my $port = shift @ARGV;

my $DEBUG=0;

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
my $data;
open(RND,"/dev/urandom");
sysread(RND,$data,1024);
close(RND);
$data=sha512_base64($data);
syswrite $cli, $data, 86;  # 86 = length(sha512_base64)
my $data1=sha512_base64($data.$secret);
warn ">>>> auth expt: $data1 <<<<\n" if ($DEBUG==1);

sysread $cli, $data, 86;
warn ">>>> auth recv: $data <<<<\n" if ($DEBUG==1);

if ($data eq $data1){
	warn ">>>> AUTH OK - GOOD TO GO <<<<\n"
}else{
	die ">>>> AUTH WRONG <<<<\n";
}

### GIVING BANNER TO THE CLIENT
$data="SSH-2.0-OpenSSH_5.1p1 Debian-7\n";
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
