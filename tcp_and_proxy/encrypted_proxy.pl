#!/usr/bin/perl

# $Id$

use strict;
use warnings;

use IO::Socket::INET;
use IO::Socket::SSL;


my $host=shift;

my $sock = IO::Socket::INET->new(PeerAddr => $host, PeerPort => '443', Proto => 'tcp');
die "Could not open socket: $!\n" unless ($sock);

my $ssl = IO::Socket::SSL->start_SSL($sock);
die "SSL problem: ",IO::Socket::SSL::errstr() unless ($ssl);

my $cmd="CONNECT 172.26.27.106:443\n";
syswrite $ssl, $cmd, length($cmd);
my $ssl_garbage;
my $ssl_num_read = sysread $ssl, $ssl_garbage, 1500;
syswrite STDOUT, $ssl_garbage, $ssl_num_read;
$ssl->stop_SSL('SSL_no_shutdown'=>1, 'SSL_ctx_free' => 1);

sleep 1;

if ( fork ) {
        my $data;
        while ( 1 ) {
                my $bytes_read = sysread $sock, $data, 1500;
                if ( not $bytes_read ) {
                        warn "No more data from ssh server - exiting.\n";
                        exit 0;
                }
                syswrite STDOUT, $data, $bytes_read;
        }
} else {
        while ( 1 ) {
                my $data;
                my $bl = sysread STDIN, $data, 1400;
                if ( not $bl) {
                        $sock->shutdown('SHUT_RDWR');
                        exit 0;
                }
                syswrite $sock, $data, $bl;
        }
}

close $sock;

