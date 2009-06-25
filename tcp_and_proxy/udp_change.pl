#!/usr/bin/perl

#
# author m.lukaszuk@gmail.com
#

use strict;
use warnings;
use integer;
use IO::Socket::INET;

my $lport=shift;
my $dport=shift;
my $MAX_TO_READ=1400;
my $data;

srand(time);

my $srv = IO::Socket::INET->new(LocalAddr => '172.30.73.133', Proto => "udp", LocalPort => $lport) or die "Couldn't be a udp server on port $lport : $!\n";

my $cli = IO::Socket::INET->new(Proto => "udp", PeerPort => $dport, PeerAddr => "127.0.0.1") or die "Couldn't create socket: $!\n";

while ($srv->recv($data, $MAX_TO_READ)) {
	if (fork()==0){
		print "$$ ######### new request ############\n";
		print "$$ >  ".time." sending it the server\n";
		$cli->send($data);
		print "$$ <  ".time." got answer\n";
		$cli->recv($data,$MAX_TO_READ);

		my $dat1=unpack('H*',$data);
		my $TTL1=rand(10000000)+30000000;
		my $TTL2=sprintf("%8x",$TTL1);
		$TTL2=~s/\s/0/g;
		$dat1=~s/c00c00010001.{8}/c00c00010001$TTL2/g;
		my $dat2=pack('H*',$dat1);
		print "$$ >  ".time." sending to the client\n";
		$srv->send($dat2);
		exit;
	}
}

