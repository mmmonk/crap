#!/usr/bin/perl

# $Id: gettech_sos.pl 144 2010-08-20 12:14:23Z m.lukaszuk $

use strict;
use warnings;
use Env;

my $file=shift;

unless (defined($file)){
  die "\nusage: $0 get_tech.txt\n\n";
}

# reading the whole file into memory
open(GT,$file);
our $gt=join('',<GT>);
close(GT);

# cleaning up the variable
$gt=~s/(\x08|\x0d|--- more ---              )//g;


# subroutines prototypes

my %task;
my %diffs;

my $in = 0;

my @high;
$high[0]="none"; $high[1]=0;
$high[2]="none"; $high[3]=0;
$high[4]="none"; $high[5]=0;
# this sorts the task based on runtime
foreach my $line (split /\n/, $gt){
  $in = 0 if ($line=~/-> get/);
  if ($line=~/-> get os/) {
    $in = 1;
    $diffs{$high[0]}=~s/>([\d\.]+)$/><font color=\"red\">$1<\/font>/ if (exists($diffs{$high[0]}));
    $diffs{$high[2]}=~s/>([\d\.]+)$/><font color=\"orange\">$1<\/font>/ if (exists($diffs{$high[2]}));
    $diffs{$high[4]}=~s/>([\d\.]+)$/><font color=\"yellow\">$1<\/font>/ if (exists($diffs{$high[4]}));
    $high[0]="none"; $high[1]=0;
    $high[2]="none"; $high[3]=0;
    $high[4]="none"; $high[5]=0;
  }
  if ($in == 1 ){
    if ($line=~/^\s+\d+\s+/){
      (my $tmp = $line)=~s/^\s+\d+\s+(.{16}?)\s*(.+?\s+){6}(.+?),\s+.*/$1|$3/;
      my @a=split(/\|/,$tmp);
      if (exists($task{$a[0]})){
        my $diff=$a[1]-$task{$a[0]};
        $diffs{$a[0]}.="</td><td>".$diff; 
        if ($a[0]!~/idle task/ and $diff > $high[1]) {
          $high[4]=$high[2];
          $high[5]=$high[3];
          $high[2]=$high[0];
          $high[3]=$high[1];
          $high[1]=$diff;
          $high[0]=$a[0];
        }
      } 
      $task{$a[0]}=$a[1];
    }
  }
}

$diffs{$high[0]}=~s/>([\d\.]+)$/><font color=\"red\">$1<\/font>/ if (exists($diffs{$high[0]}));
$diffs{$high[2]}=~s/>([\d\.]+)$/><font color=\"orange\">$1<\/font>/ if (exists($diffs{$high[2]}));
$diffs{$high[4]}=~s/>([\d\.]+)$/><font color=\"yellow\">$1<\/font>/ if (exists($diffs{$high[4]}));

print "<table CLASS=\"head1\" border=\"1\" frame=\"border\" align=\"center\">\n";
my $row=1;
foreach my $name (sort keys %diffs){
  if ($row==1){
    print "<tr CLASS=\"row1\">";
    $row=0;
  }else{
    print "<tr CLASS=\"row2\">";
    $row=1;
  }
  print "<td><b>$name</b> ".$diffs{$name}."</td></tr>\n";
}
print "</table>";
