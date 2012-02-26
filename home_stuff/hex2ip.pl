#!/usr/bin/perl -wW

use strict;

my $ip = shift;

exit unless ($ip);

my $nip;
$nip = $ip;
$nip =~ s/\s+//g;
$nip =~ s/(..)(..)(..)(..)/$1;$2;$3;$4/;
my @tmp = split( ';', $nip );

$tmp[0] = hex( $tmp[0] );
$tmp[1] = hex( $tmp[1] );
$tmp[2] = hex( $tmp[2] );
$tmp[3] = hex( $tmp[3] );

$nip = join( '.', @tmp );

print "$ip - $nip\n";
