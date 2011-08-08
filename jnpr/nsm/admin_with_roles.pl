#!/usr/bin/perl

# $Id$

use strict;
use warnings;
use integer;

my $guiutils="/usr/netscreen/GuiSvr/utils/";
my $dbroot="/usr/netscreen/GuiSvr/var/xdb/data/";
my $queryfile="/tmp/dbxml_adminrole_query.txt";
my $dbver;

opendir(DIR,$guiutils) or die "Can't read dir $guiutils.\n";
while(my $node=readdir(DIR)){
  next unless ($node=~/dbxml/);
  $dbver=$node;
}
closedir(DIR); 

die "Can't find valid dbxml version, exiting\n" unless ($dbver); 

my $dbxmlpath="$guiutils/$dbver/";
$ENV{LD_LIBRARY_PATH}="$dbxmlpath/lib:";

umask(0077);

sub dbxmlquery{
  my $container=shift;
  my $query=shift;

  open(Q1,"> $queryfile") or die "Can't create file: $queryfile\n";
  print Q1 "openContainer \"$container\"
setQueryTimeout 10
query 'collection()/$query'
print
quit";
  close(Q1);

  open(CMD,"$dbxmlpath/bin/dbxml -h $dbroot -s $queryfile |") or die "Can't run command: $!";
  my @data=<CMD>;
  close(CMD);
  unlink($queryfile);
  return @data;
}

unlink($queryfile) if ( -f $queryfile);
my @res = dbxmlquery("admin","__[dbxml:metadata(\"HighDbVerID\")=65520]");

my %admin;
my ($name,$perms);
foreach (@res){
  next if (/^Joined/);
  $name = $1 if (/^\<__\>\<\!\[CDATA\[(.+?)\]\]\>/);
  $perms = $1 if (/\<perms\>(.+?)\<\/perms\>/);
  my @roles = $perms=~/CDATA\[\&(\d+\.role\.\d+)\].*?\[CDATA\[(\d+)\]\]/g;
  $admin{$name} = join(':',@roles);
}

my (%rolenames,%domains,$tname);
foreach my $name (sort keys %admin){
  my @roles = split(":",$admin{$name});
  my @trols = ();
  for(my $i=0;$i<scalar(@roles)-1;$i+=2) {
    if (!exists($rolenames{$roles[$i]})){
      (my $objid=$roles[$i])=~s/\d+.role.(\d+)/$1/;
      @res = dbxmlquery("role","__[dbxml:metadata(\"ObjectID\")=$objid and dbxml:metadata(\"HighDbVerID\")=65520]");
      foreach (@res){
        next if (/^Joined/);
        $tname=$1 if (/^\<__\>\<\!\[CDATA\[(.+?)\]\]\>/);
      }
      $rolenames{$roles[$i]}=$tname;
    }
    if (!exists($domains{$roles[$i+1]})){
      @res = dbxmlquery("domain","__[dbxml:metadata(\"ObjectID\")=".$roles[$i+1]." and dbxml:metadata(\"HighDbVerID\")=65520]");
      foreach (@res){
        next if (/^Joined/);
        $tname=$1 if (/^\<__\>\<\!\[CDATA\[(.+?)\]\]\>/);
      }
      $domains{$roles[$i+1]}=$tname;
    }  
    push(@trols,"\"".$rolenames{$roles[$i]}."\"@\"".$domains{$roles[$i+1]}."\"");
  }
  print "$name - ".(join(",",@trols))."\n";
}
