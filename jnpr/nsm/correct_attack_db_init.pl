#!/usr/bin/perl

# $Id$

use strict;
use warnings;
use integer;

my $bad_version='"idp4.1.110090831"';

my @tags;
my $skip=0;
my $top=1;
my $fr=1;
my $atleastone=0;
my $depth=0;

my $file=shift;
open(FD,$file) or die "error: $!\n";
while(<FD>){
  next if (/^END\s*$/);
  $top=0 if (/^\(/);
  next if ($top==1);
  $skip=1 if (/^\s+:description \(/);
  $skip=0 if (/^\s+\)\s*$/);
  if ($skip==1){
    print;
    next;
  }
  push (@tags,$_) if (/(^\s*(:\S*\s)?\(|\(\s*$)/);
  pop (@tags) if (/(^\s*\)|\)\s*$)/);
  next if (/^\)/);
  if (/^\(/){
    chomp;
    if ($fr==0){
      print "#####TUPLE_DATA_END#####\n#####TUPLE_DATA_BEGIN#####\n";
    }else{
      print "#####TUPLE_DATA_BEGIN#####\n";
      $fr=0;
    }
    s/^\((........)(....)(....)$/$1-$3/;
    my @a=map(hex,split('-'));
    print "$a[0]\n$a[1]\n";
    next;
  }
  if (/^\t:\d+\s+(\(.+)$/){
	print $1."\n";
 	next;
  }
  if ($tags[1] and $tags[1]=~/CS:/){
    if ($tags[$#tags] and $tags[$#tags]=~/supported-on/){
      unless (/$bad_version/){
        print;
        $atleastone=1;
      }
      $depth=$#tags;
    }else{
      if ($depth > 0 and $depth ne $#tags-1){
        if ($atleastone==0){
 	  print "                                        : (\"idp4.1.0\")\n";
        }
        $atleastone=0;
        $depth=0;
      }
      print;
    }
  }else{
    print;
  }
}
print "#####TUPLE_DATA_END#####\n";
close(FD);

