#!/usr/bin/perl -wW

use strict;

my $ip = shift;

exit unless ($ip);

my $nip;
$nip = $ip;
$nip =~ s/(\d+)\.(\d+)\.(\d+)\.(\d+)/$1;$2;$3;$4/;
my @tmp = split( ';', $nip );

my @hex;
$hex[0] = sprintf( "%02x", $tmp[0] );
$hex[1] = sprintf( "%02x", $tmp[1] );
$hex[2] = sprintf( "%02x", $tmp[2] );
$hex[3] = sprintf( "%02x", $tmp[3] );

my @bin;
$bin[0] = pack('B', $tmp[0] );

$nip = join( '', @hex);

print "$nip - $ip\n";
