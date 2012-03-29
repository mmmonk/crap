#!/usr/bin/perl

use warnings;
use strict;
use integer;

my $file=shift;

unless ($file){
  print "usage: $0 xdif_file_name\n\nThe modified output will be printed to standard output\n\n";
  exit 1;
}

my %max;
my %seen;
my %link;
my @stack;
my $rbfwoffset = 0;
my $inrbfw = 0;

open(FD,$file) or die "$!";
while(<FD>) {

  print if ($inrbfw == 0);
  if (/^rb_firewall/) {
    $inrbfw = 1;
    $rbfwoffset = tell(FD);
    $rbfwoffset = ($rbfwoffset<=50) ? 0 : $rbfwoffset-50;
  }
  
  if ($inrbfw == 1) {
    if (/^\t+:.+?\(/) {
      push(@stack,$_);
    }
    pop(@stack) if (/\)\s*$/);
    
    if (/\t+:preferred-id \((\d+)\)/) {
      my $ruleId = $1;
      if ($stack[0] =~ /\t+:(\d+) \(/) {
        my $policyId = $1;
        if (exists($max{$policyId})) {
          $max{$policyId} = $ruleId if ($max{$policyId} < $ruleId);
        }else{
          $max{$policyId} = $ruleId;
        }
        if (exists($seen{"$policyId-$ruleId"})){
          $seen{"$policyId-$ruleId"} += 1;
        } else {
          $seen{"$policyId-$ruleId"} = 1;
        }
      }
    }

    if (/\t+:link \(\".+?rb_firewall\.(\d+)\"/) {
      my $linkId = $1;
      if ($stack[0] =~ /\t+:(\d+) \(/) {
        my $policyId = $1;
        if (exists($link{$linkId})) {
          die "shit happend - $linkId - $policyId\n";
        } else {
          $link{$linkId} = $policyId;
        }
      }
    }
  }

  if ($inrbfw == 1 and /^END/) {
    $inrbfw = 0;
    last;
  }
}

seek(FD,$rbfwoffset,0);

@stack = ();

my $spam = 0;
while(<FD>) {
  $inrbfw = 0 if (/^END/);
  if (/^rb_firewall/) {
    $inrbfw = 1;
    $spam = 1;
  }
  if ($inrbfw == 1) {
    if (/\t+:.+?\(/) {
      push(@stack,$_);
    }
    pop(@stack) if (/\)\s*$/);
    if (/^\t+:preferred-id \((\d+)\)/) {
      my $ruleId = $1;
      if ($stack[0] =~ /\t+:(\d+) \(/) {
        my $policyId = $1;
        if (exists($link{$policyId})) { 
          my $ppId = $link{$policyId};
          if (exists($seen{"$ppId-$ruleId"})) {
            my $nrId = 1;
            while (exists($seen{"$ppId-$nrId"})) {
              $nrId++;
            }
            $seen{"$ppId-$nrId"} = 1;
            s/(\t+:preferred-id \().+?(\).*)/$1$nrId$2/;
            $seen{"$policyId-$ruleId"} -= 1;
            delete($seen{"$policyId-$ruleId"}) if ($seen{"$policyId-$ruleId"} == 0);
            $max{$ppId}=$nrId if ($max{$ppId} < $nrId);
          }
        }elsif (exists($seen{"$policyId-$ruleId"}) and $seen{"$policyId-$ruleId"} > 1){
          my $nrId = 1;
          while (exists($seen{"$policyId-$nrId"})) {
            $nrId++;
          }
          $seen{"$policyId-$nrId"} = 1;
          s/(\t+:preferred-id \().+?(\).*)/$1$nrId$2/;
          $seen{"$policyId-$ruleId"} -= 1;
          delete($seen{"$policyId-$ruleId"}) if ($seen{"$policyId-$ruleId"} == 0);
          $max{$policyId}=$ruleId if ($max{$policyId} < $ruleId);
        }
      }
    }
    if (/^\t+:next_preferred_id/ and $stack[0] =~ /\t+:(\d+) \(/){
      my $policyId = $1;
      if (exists($max{$policyId})) {
        my $maxId = $max{$policyId} + 1;
        s/(\t+:next_preferred_id \().+?(\).*)/$1$maxId$2/;
      }
    }
  }

  print if ($spam == 1);
}

close(FD);
