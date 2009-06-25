#!/usr/bin/perl -W

# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
# Copyright (c) 2005, Marek £ukaszuk 
# BSD License at http://monkey.geeks.pl/bsd/

use Net::DNS;
use LWP::UserAgent;

use strict;

sub sblquery;
sub dsblrm;

my $r = Net::DNS::Resolver->new;

$r->nameservers('127.0.0.1');

my @ips  = ();
my %done = ();

for ( my $i = 192 ; $i <= 255 ; $i++ ) {
    for ( my $j = 1 ; $j <= 255 ; $j++ ) {
        push( @ips, "192.168.$i.$j" );
    }
}

srand( time ^ $$ );

my $max = $#ips;
for ( my $i = 0 ; $i <= $max ; $i++ ) {
    my $rnd;
    do {
        $rnd = int( rand( $max + 1 ) );
    } while ( exists( $done{$rnd} ) );
    $done{$rnd} = 1;

    sblquery( $r, "list.dsbl.org", $ips[$rnd], $i, $max );
}

sub sblquery() {
    my $res = shift;
    my $sbl = shift;
    my $qip = shift;
    my $ai  = shift;
    my $am  = shift;

    my $oip = $qip;
    return "err" unless ( $qip =~ /^\d+\.\d+\.\d+\.\d+$/ );
    $qip =~ s/^(\d+)\.(\d+)\.(\d+)\.(\d+)$/$4.$3.$2.$1/;

    my $dnspak = $res->query( "$qip.$sbl.", 'TXT' );
    return "null" unless ($dnspak);

    foreach my $ans ( $dnspak->answer ) {
        next unless $ans->type eq "TXT";
        my $anstxt = $ans->string;
        next unless ( $anstxt =~ /http:\/\/dsbl\.org\/listing/ );

        #		print $anstxt."\n";
        dsblrm( $oip, $ai, $am );
        my $sleep = int( rand(30) );
        sleep($sleep);
    }
}

sub dsblrm() {
    my $qip = shift;
    my $bi  = shift;
    my $bm  = shift;

    my $ua = LWP::UserAgent->new;
    $ua->agent(
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0; .NET CLR 1.1.4322");
    my $req =
      HTTP::Request->new(
        GET => "http://dsbl.org/removal2?ip=$qip&email=postmaster%40microsoft.com" )
      ;
    my $res = $ua->request($req);
    return unless ( $res->is_success );
    my $out = join( " ", $res->content );

    if ( $out =~ /(\d+\.){3}\d+ accepted message/ ) {
        print "[$bi/$bm] $qip confirmation email sent\n";
    }
    else {
        print "[$bi/$bm] $qip error\n";
    }
}
