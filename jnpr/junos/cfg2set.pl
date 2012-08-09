#!/usr/bin/perl

# $Id: 20120809$
# $Date: 2012-08-09 13:26:12$
# $Author: Marek Lukaszuk$

use strict;
use integer;
use warnings;

sub printset {
  my $aref = shift;
  my @n = @$aref;
  my $txt = "set ";
  
  return "" if (length(@n) == 0);
  
  foreach my $a (@n){
    $txt .= $a." ";
  }
 
  return $txt;
}

my $notprinted = 0;
my @n;
while(<>){
  chomp;
  s/(\r|\n)//g;
  s/^\s*//;
  s/;\s*$//;
  if (/\{\s*$/){
    s/^(.+?)\s+\{/$1/;
    push(@n,$1);
    $notprinted = 1;
  }elsif (/^\s*\}\s*$/) {
    print printset(\@n),"\n" if ($notprinted == 1); 
    $notprinted = 0;
    pop(@n);
  }else{
    print printset(\@n),"$_\n";
    $notprinted = 0;
  }
}
