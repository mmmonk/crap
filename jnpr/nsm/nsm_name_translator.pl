#!/usr/bin/perl

# $Id$ 

use strict;
use warnings;

# getting GET values
my %params=map{my($name,$value)=split/\=/;$name => $value} map{split /\&/} $ENV{"QUERY_STRING"};

my $pagetitle="NSM name translator";

my %nsm;
#loading NSM naming file
open(FD,"/home/www/perl/nsm_naming.txt") or die "can't load file\n";
while(<FD>){
  next unless ($_);
  chomp;
  my ($a,$b)=split(" ");
  $nsm{$a}=$b;
}
close(FD);

# we start output here
print "Content-type: text/html\n\n\
<html>\
<head>\
<title>$pagetitle</title>\
</head>\
<body> 
<h1 align=\"center\"><a href=\"?\">$pagetitle</a></h1>\n";

print "<table width=\"90%\" border=\"0\" align=\"center\">\
<form method=\"get\" enctype=\"multipart/form-data\">\
<tr><td align=\"right\">NSM version (in LGB format):</td><td><input type=\"text\" name=\"q\" value=\"";
print $params{'q'} if (exists($params{'q'}));
print "\"/></td></tr>\
<tr><td>&nbsp;</td><td><input type=\"submit\" value=\"search\"/></td></tr>\n";
print "</form>\n</table></br>";
if (exists($params{'q'}) and $params{'q'} ne ""){
  my $shit=$params{'q'};
  $shit=~s/lgb/LGB/i;
  if ($shit=~/(LGB\d+z\d+)(.*)/){
    my $v=$1;
    my $p=$2; 
    if (exists($nsm{$v})){
      $shit=~/LGB(\d+)z(\d+)(.*)/; 
      print "<p align=\"center\">query: $shit<br/>main release: ".$nsm{$v}."<br/>GNATS release: ".$nsm{$v}."-".$1.".".$2.$3."<br/></p>";
    }else{
      print "<p align=\"center\">not in the local db</p>";
    }
  }else{
    print "<p align=\"center\">wrong format of the name it should be something like LGB14z3s1</p>";
  }
}


print "<p align=\"center\"><a href=\"mailto:mlukaszuk\@juniper.net\">complains/ideas/money</a></p></body></html>\n";

