#!/usr/bin/perl

# $Id: 20121104$
# $Date: 2012-11-04 18:52:38$
# $Author: Marek Lukaszuk$
#
# script used to show a simple page with all the
# information that browser sends, plus src IP

use strict;
use warnings;


if (exists($ENV{"REMOTE_ADDR"}) and exists($ENV{"HTTP_HOST"})){
  if ($ENV{"REMOTE_ADDR"}=="::1" or $ENV{"REMOTE_ADDR"}=="127.0.0.1"){
    print "Status: 301 Moved Permanently\n";
    print "Location: http://".$ENV{"HTTP_HOST"}."\n\n";
  }
}

print "Content-type: text/plain\n\n";
for my $k (reverse sort keys %ENV){
  if ($k=~/^(HTTP_|REMOTE_|REQUEST_)/){
    my $a = $k;
    $a =~ s/(HTTP_|REMOTE_|REQUEST_)//;
    $a =~ s/_/-/g;
    $a = lc($a);

    print "$a: ".$ENV{$k}."\n";
  }
}

