#!/usr/bin/perl

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

open(Q1,"> $queryfile") or die "Can't create file: $queryfile\n";
print Q1 "openContainer \"admin\"
setQueryTimeout 10
lookupIndex node-metadata-equality-decimal \"\" HighDbVerID 65520
print
quit";
close(Q1);

my %admin;
my ($name,$perms);
open(CMD,"$dbxmlpath/bin/dbxml -h $dbroot -s $queryfile |");
while(<CMD>){
  next if (/^Joined/);
  $name=$1 if (/^\<__\>\<\!\[CDATA\[(.+?)\]\]\>/);
  $perms=$1 if (/\<perms\>(.+?)\<\/perms\>/);
  my @roles = $perms=~/\&(\d+\.role\.\d+)/g;
  $admin{$name}=join(':',@roles);
}
close(CMD);
unlink($queryfile);

my %rolenames;
foreach my $name (sort keys %admin){
  my @roles=split(":",$admin{$name});
  my @troles=();
  foreach my $role (@roles){
    if (!exists($rolenames{$role})){
      (my $objid=$role)=~s/\d+.role.(\d+)/$1/;
      open(Q1,"> $queryfile") or die "Can't create file: $queryfile\n";
      print Q1 "openContainer \"role\"
setQueryTimeout 10
lookupIndex node-metadata-equality-decimal \"\" ObjectID $objid 
print
quit";
      close(Q1);
      open(CMD,"$dbxmlpath/bin/dbxml -h $dbroot -s $queryfile |");
      my $name=$role;
      while(<CMD>){
        next if (/^Joined/);
        $name=$1 if (/^\<__\>\<\!\[CDATA\[(.+?)\]\]\>/);
      }
      $rolenames{$role}=$name;
      close(CMD);
      unlink($queryfile);
    }  
    push(@troles,$rolenames{$role});
  }
  print "$name - ".(join(",",@troles))."\n";
}
