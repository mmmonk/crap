#!/usr/bin/perl

use strict;
use warnings;
use integer;

my $vpn_tunnel_id = shift;
my $config = shift;

my %vpnid;
my %gw;
my %vpn;

open(FD,$vpn_tunnel_id) or die "$!";
while(<FD>){
  next unless (/^(\d+) (\S+)\s*$/);
  $vpnid{$2}=$1;
}
close(FD);

my $in_ike = "none";
my $in_ipsec = "none";
my $last = "";
open(FD,$config) or die "$!";
while(<FD>) {
  $in_ike = $1 if (/^(\s+)ike {\s*$/);
  $in_ike = "none" if (/^$in_ike}\s*$/);
  if ($in_ike ne "none") {
    $last = $1 if (/^\s+gateway (\S+) {\s*$/);
    $gw{$last} = $1 if (/^\s+address (\S+);/);
  }
  $in_ipsec = $1 if (/^(\s+)ipsec {\s*$/);
  $in_ipsec = "none" if (/^$in_ipsec}\s*$/);
  if ($in_ipsec ne "none") {
    $last = $1 if (/^\s+vpn (\S+) {\s*$/);
    $vpn{$last} = $1 if (/^\s+gateway (\S+);/);
  }
}
close(FD);

foreach my $name (sort keys %vpnid) {
  next unless ($vpnid{$name} and $vpn{$name});
  my $gateway = $vpn{$name};
  next unless ($gw{$gateway});
  my $address = $gw{$gateway};
  print "$vpnid{$name} $name $gateway $address\n";
}
