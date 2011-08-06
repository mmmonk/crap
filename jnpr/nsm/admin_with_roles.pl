#!/usr/bin/perl

# $Id$

use strict;
use warnings;
use integer;

my $guiutils="/usr/netscreen/GuiSvr/utils/";
my $dbroot="/usr/netscreen/GuiSvr/var/xdb/data/";
my $queryfile="/tmp/dbxml_adminrole_query.txt";

my $dbver;

opendir(DIR,$guiutils);
while(my $node=readdir(DIR)){
  next unless ($node=~/dbxml/);
  $dbver=$node;
}
closedir(DIR); 

my $dbxmlpath="$guiutils/$dbver/";

$ENV{LD_LIBRARY_PATH}="$dbxmlpath/lib:";

if ( -f $queryfile){
  unlink($queryfile);
}

umask(0077);
open(Q1,"> $queryfile") or die "Can't create file: $queryfile\n";
print Q1 "openContainer \"admin\"
setQueryTimeout 10
query 'collection()/__[dbxml:metadata(\"HighDbVerID\")=65520]'
print
quit";
close(Q1);

# <__><![CDATA[&0.role.79]]><domains><__><![CDATA[1]]></__></domains></__>

my %admin;
my ($name,$perms);
open(CMD,"$dbxmlpath/bin/dbxml -h $dbroot -s $queryfile |");
while(<CMD>){
  next if (/^Joined/);
  $name=$1 if (/^\<__\>\<\!\[CDATA\[(.+?)\]\]\>/);
  $perms=$1 if (/\<perms\>(.+?)\<\/perms\>/);
  my @roles = $perms=~/CDATA\[\&(\d+\.role\.\d+)\].*?\[CDATA\[(\d+)\]\]/g;
  $admin{$name}=join(':',@roles);
}
close(CMD);
unlink($queryfile);

my %rolenames;
my %domains;
foreach my $name (sort keys %admin){
  my @roles=split(":",$admin{$name});
  my @troles=();
  for(my $i=0;$i<scalar(@roles)-1;$i+=2) {
    if (!exists($rolenames{$roles[$i]})){
      (my $objid=$roles[$i])=~s/\d+.role.(\d+)/$1/;
      open(Q1,"> $queryfile") or die "Can't create file: $queryfile\n";
      print Q1 "openContainer \"role\"
setQueryTimeout 5 
query 'collection()/__[dbxml:metadata(\"ObjectID\")=$objid and dbxml:metadata(\"HighDbVerID\")=65520]'
print
quit";
      close(Q1);
      open(CMD,"$dbxmlpath/bin/dbxml -h $dbroot -s $queryfile |");
      my $name=$roles[$i];
      while(<CMD>){
        next if (/^Joined/);
        $name=$1 if (/^\<__\>\<\!\[CDATA\[(.+?)\]\]\>/);
      }
      $rolenames{$roles[$i]}=$name;
      close(CMD);
      unlink($queryfile);
    }
    if (!exists($domains{$roles[$i+1]})){
      open(Q1,"> $queryfile") or die "Can't create file: $queryfile\n";
      print Q1 "openContainer \"domain\"
setQueryTimeout 5
query 'collection()/__[dbxml:metadata(\"ObjectID\")=".$roles[$i+1]." and dbxml:metadata(\"HighDbVerID\")=65520]'
print
quit";
      close(Q1);
      open(CMD,"$dbxmlpath/bin/dbxml -h $dbroot -s $queryfile |");
      my $name=$roles[$i+1];
      while(<CMD>){
        next if (/^Joined/);
        $name=$1 if (/^\<__\>\<\!\[CDATA\[(.+?)\]\]\>/);
      }
      $domains{$roles[$i+1]}=$name;
      close(CMD);
      unlink($queryfile);
    }  
    push(@troles,"\"".$rolenames{$roles[$i]}."\"@\"".$domains{$roles[$i+1]}."\"");
  }
  print "$name - ".(join(",",@troles))."\n";
}
