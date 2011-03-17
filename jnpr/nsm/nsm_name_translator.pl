#!/usr/bin/perl

# $Id$ 

use strict;
use warnings;

# getting GET values
my %params=map{my($name,$value)=split/\=/;$name => $value} map{split /\&/} $ENV{"QUERY_STRING"};

my $pagetitle="NSM name translator";

my %nsm = (
'LGB7z1' => '2007.1r1',
'LGB7z2' => '2007.1r2',
'LGB7z3' => '2007.1r3',
'LGB8z1' => '2007.2r1',
'LGB8z1' => '2007.2r1',
'LGB8z2' => '2007.2r2',
'LGB8z2' => '2007.2r2',
'LGB9z1' => '2007.3r1',
'LGB9z2' => '2007.3r2',
'LGB9z3' => '2007.3r3',
'LGB9z4' => '2007.3r4',
'LGB9z5' => '2007.3r5',
'LGB10z1' => '2008.1r1',
'LGB10z2' => '2008.1r2',
'LGB11z1' => '2008.2r1',
'LGB11z2' => '2008.2r2',
'LGB12z1' => '2009.1r1',
'LGB12z2' => '2010.1r1',
'LGB13z1' => '2010.2r1',
'LGB14z1' => '2010.3r1',
'LGB14z2' => '2010.4r1',
'LGB14z3' => '2011.1r1'
);

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

