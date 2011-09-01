#!/usr/bin/perl
#
# $Id$
#

# based on:
# http://googleonlinesecurity.blogspot.com/2011/04/improving-ssl-certificate-security.html

use strict;
use warnings;
use integer;
use POSIX; 

my $domain=shift;

open(SHA,"openssl s_client -connect $domain:443 < /dev/null 2>/dev/null | openssl x509 -outform DER | openssl sha1 |");
my $sha=<SHA>;
close(SHA);
$sha=~s/^.*?(\S+)$/$1/;
chomp $sha;
open(DIG,"dig +short $sha.certs.googlednstest.com TXT |");
my $times=<DIG>;
close(DIG);
$times=~s/"//g;
chomp $times;
my @days=split(" ",$times);

print "domain........: $domain\n";
print "cert sha1 fp..: $sha\n";
print "first seen on.: ".(asctime(localtime($days[0]*86400)));
print "last seen on..: ".(asctime(localtime($days[1]*86400)));
print "seen on #days.: ".$days[2]."\n";
