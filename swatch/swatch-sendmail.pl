#!/usr/bin/perl -wW

# $Id$





use strict;
use integer;

my $to=shift;
my $subject=join(' ',@ARGV);

my $sendmail="/usr/sbin/sendmail";


my @in=<STDIN>;
my $text=join('',@in);

my $host=(split(" ",$text))[3];


my $msg="To: <netteam\@somecompany.com>
Content-Type: text/plain;
	charset=\"iso-8859-2\"
From: <netteam\@somecompany.com>
Subject: [swatch] - $host - $subject

$text
";

open(SENDMAIL, "| $sendmail -oi -t -f 'netteam\@somecompany.com'" ) or die "Can't open sendmail: $!\n";
print SENDMAIL $msg;
close(SENDMAIL) or warn "Sendmail didn't close nicely: $!\n";

