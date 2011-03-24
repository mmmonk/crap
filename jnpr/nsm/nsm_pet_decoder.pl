#!/usr/bin/perl

# $Id$ 

use strict;
use warnings;

# getting GET values
my %params=map{my($name,$value)=split/\=/;$name => $value} map{split /\&/} $ENV{"QUERY_STRING"};



my $pagetitle="NSM PET decoder";

# we start output here
print "Content-type: text/html\n\n\
<html>\
<head>\
<title>$pagetitle</title>\
</head>\
<body> 
<h1 align=\"center\"><a href=\"?\">$pagetitle</a></h1>
<p align=\"center\">this informatio is located in the source code in the file:<br/>
server/c/libs/mgtServer/serverCore/include/connectionMgr.h</p>\n";

print "<table width=\"90%\" border=\"0\" align=\"center\">\
<form method=\"get\" enctype=\"multipart/form-data\">\
<tr><td align=\"right\">PET code:</td><td><input type=\"text\" name=\"q\" value=\"";
print $params{'q'} if (exists($params{'q'}));
print "\"/></td></tr>\
<tr><td>&nbsp;</td><td><input type=\"submit\" value=\"deocde\"/></td></tr>\n";
print "</form>\n</table></br>";
if (exists($params{'q'}) and $params{'q'} ne ""){
  my $pet=$params{'q'};
  $pet=~s/^0x//;
  my $ans="";

  if (length($pet)<8){
    $ans="fake PET - letters \"TLS\" in ascii" if ($pet eq "544c53");
    $ans="fake PET - letters \"SSH\" in ascii" if ($pet eq "535348");
  }else{
    if ($pet eq "47544c53"){
      $ans="fake PET - letters \"GTLS\" in ascii";
    }elsif ($pet=~/^81/){
      $ans="DEV ";
      $ans.="NSPAGENT " if ($pet=~/1..$/);
      $ans.="no encryption " if ($pet=~/1$/);
      $ans.="MTM encryption " if ($pet=~/2$/);
    }elsif ($pet=~/^82/){
      $ans="IDP ";
    }elsif ($pet=~/^83/){
      $ans="GUI client ";
      $ans.="authentication disabled " if ($pet=~/1..$/);
      $ans.="authentication use Radius server " if ($pet=~/2..$/);
      $ans.="local authentication " if ($pet=~/3..$/);
      $ans.="auto authentication method " if ($pet=~/4..$/);
      $ans.="no encryption " if ($pet=~/1$/);
      $ans.="hunny encryption " if ($pet=~/2$/);
      $ans.="htm encryptioni " if ($pet=~/3$/);
    }elsif ($pet=~/^84/){
      $ans="Internal communication ";
      $ans.="GDH " if ($pet=~/01..$/);
      $ans.="loopback-csp " if ($pet=~/02..$/);
      $ans.="SRV_DD " if ($pet=~/03..$/);
      $ans.="SVR_DDH " if ($pet=~/04..$/);
      $ans.="Rollup Log Database " if ($pet=~/05..$/);
      $ans.="Log Receiver " if ($pet=~/06..$/);
      $ans.="Log Walker " if ($pet=~/07..$/);
      $ans.="Status Receiver " if ($pet=~/08..$/);
      $ans.="Debugging and test " if ($pet=~/09..$/);
      $ans.="Master Cylinder " if ($pet=~/0a..$/i);
      $ans.="SVR_GSSC " if ($pet=~/0b..$/i);
      $ans.="SVR_DSSC " if ($pet=~/0c..$/i);
      $ans.="SVR_DC " if ($pet=~/0d..$/i);
      $ans.="GuiSvr CLI " if ($pet=~/0e..$/i);
      $ans.="DevSvr CLI " if ($pet=~/0f..$/i);
      $ans.="ProfilerMgr " if ($pet=~/10..$/);
      $ans.="Log Migration " if ($pet=~/11..$/);
      $ans.="DevSvrHaMgr " if ($pet=~/12..$/);
      $ans.="HA master replication " if ($pet=~/13..$/);
      $ans.="Central manager " if ($pet=~/14..$/);
      $ans.="highAvail server "  if ($pet=~/15..$/);
      $ans.="License Manager " if ($pet=~/16..$/);
      $ans.="NBIService Component Mgr " if ($pet=~/20..$/);
      $ans.="SVR_TEST_CM " if ($pet=~/21..$/);
      $ans.="SVR_JVM " if ($pet=~/22..$/);

      $ans.="no encryption " if ($pet=~/1$/);
      $ans.="MTM encryption " if ($pet=~/2$/);
    }else{
      $ans="no idea";
    }
  }
  print "<p align=\"center\"><b>0x$pet</b> is <u>$ans</u></p>\n";
}


print "<p align=\"center\"><a href=\"mailto:mlukaszuk\@juniper.net\">complains/ideas/money</a></p></body></html>\n";

