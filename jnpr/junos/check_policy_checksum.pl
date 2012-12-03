#!/usr/bin/perl

# $Id: 20121128$
# $Date: 2012-11-28 12:39:29$
# $Author: Marek Lukaszuk$

use strict;
use warnings;

my %chpol;
my %pol;
my $inside_RE = 0;
my $lsys = "";
my $spu = "";


while(<>){

  $inside_RE = 1 if (/> show security policies checksum/);

  $inside_RE = 0 if ($inside_RE == 1 and /^\s*$/);

  if ($inside_RE == 1){

    $lsys = $1 if (/Logical system: (\S+)\s*$/);

    if (/0x/){ # only hex values
      my @a = split(" ");
      $chpol{$lsys."#".$a[0]."#".$a[1]} = $a[2]
    }
  }

  if (/======== Start (SPU.+) ========/) {
    $spu = $1;
    %pol = %chpol;
  }

  if ($spu ne "" and /======== End SPU/) {
    for my $k (keys %pol){
      my @a=split("#");
      print "missing on SPU: $spu, lsys:$a[0] from:$a[1] to:$a[2]\n";
    }
    $spu = "";
  }

  unless ($spu eq ""){

    $lsys = $1 if (/Logical system: (\S+)\s*$/);

    if (/0x/){ # only hex values
      my @a = split(" "); # 0-from 1-to 2-checksum

      if (exists($chpol{$lsys."#".$a[0]."#".$a[1]})){
        delete($pol{$lsys."#".$a[0]."#".$a[1]});
        my $c = $chpol{$lsys."#".$a[0]."#".$a[1]};

        unless ($c eq $a[2]){
          print "chcksm doesn't match: $spu lsys:$lsys from:$a[0] to:$a[1] RE:$c SPU:$a[2]\n";
        }

      } else {
        print "missing on RE: $spu lsys:$lsys from:$a[0] to:$a[1]\n";
      }
    }
  }
}
