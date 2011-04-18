#!/usr/bin/perl

# $Id$

use strict;
use warnings;
use integer;

use Net::RawIP;


my ($src,$rp,$if);

# some defaults values
#
my $dst="224.0.1.40";
my $sleep=1;
my $count=1;
my $htime=181;
my $ttl=5;
my @gaddr=();

sub usage{
  print "
usage: $0 -d <destination IP> -rp <rendezvous point IP> <more options>

  packet is being send according to:
  ftp://ftp.icm.edu.pl/packages/cisco-ipmulticast/pim-autorp-spec01.txt

  options:
  -rp <IP>
    rendezvous point IP - required,

  -I <interface>
    interface name - required when destination is multicast address,

  -d <IP>
    destination IP for the packet - default is 224.0.1.40,

  -g <groupaddress/bitmask>
    group address, can be specified more then once, if prefixed 
    with '-' (minus) this will be a negative group address, 
    if not set the default value is: -224.0.0.0/4 

  -s <IP>
    source IP, by default handled by the OS,

  -ht <seconds>
    holddown timer, default value is ".$htime." seconds,

  -t <ttl>
    TTL value of the IP packet, default value is ".$ttl.",

  -c <integer>
   number of packets to send, default value is ".$count.",

  -i <seconds>
   how long to wait in seconds between sending each packet,
   default value is ".$sleep.",
";
  exit;
}

usage if ($#ARGV==0);

for(my $i=0;$i<$#ARGV;$i+=2){
  if($ARGV[$i] eq "-s" and exists($ARGV[$i+1])){ $src=$ARGV[$i+1]; next;}
  if($ARGV[$i] eq "-d" and exists($ARGV[$i+1])){ $dst=$ARGV[$i+1]; next;}
  if($ARGV[$i] eq "-rp" and exists($ARGV[$i+1])){ $rp=$ARGV[$i+1]; next;}
  if($ARGV[$i] eq "-ht" and exists($ARGV[$i+1])){ $htime=$ARGV[$i+1]; next;}
  if($ARGV[$i] eq "-t" and exists($ARGV[$i+1])){ $ttl=$ARGV[$i+1]; next;}
  if($ARGV[$i] eq "-c" and exists($ARGV[$i+1])){ $count=$ARGV[$i+1]; next;}
  if($ARGV[$i] eq "-I" and exists($ARGV[$i+1])){ $if=$ARGV[$i+1]; next;}
  if($ARGV[$i] eq "-i" and exists($ARGV[$i+1])){ $sleep=$ARGV[$i+1]; next;}
  if($ARGV[$i] eq "-g" and exists($ARGV[$i+1])){ push(@gaddr,$ARGV[$i+1]); next;}
  usage; 
}

usage if (!defined($dst) or !defined($rp));

push(@gaddr,"-224.0.0.0/4") if($#gaddr==-1);

# payload definition 
# ftp://ftp.icm.edu.pl/packages/cisco-ipmulticast/pim-autorp-spec01.txt

# version 1 type 2 | rp count 1
my @data = (     
  0x12,0x01
);

if ($htime>255){
  push(@data,($htime/256));
}else{
  push(@data,0);
}
push(@data,($htime%256));

# reserved bits
push(@data,(
  0x00,0x00,0x00,0x00  
));                     

# RP
push(@data,split('\.',$rp)); 

# RP highest PIM version - 11 : Dual version 1 and 2 
push(@data,0x03);

# number of group addresses
push(@data,$#gaddr+1);

# group addresses
foreach (@gaddr){
  if (/^-/){
    push(@data,0x01);
    s/^-//;
  }else{
    push(@data,0x00);
  }
  my @g=split('/');
  push(@data,$g[1]);
  push(@data,split('\.',$g[0]));
}

# finally creating the packet
my $a= Net::RawIP->new(
  {ip => {daddr => $dst, ttl=>$ttl},
  udp => {source => 496,dest => 496, data => pack "C*",@data}}
);

$a->set({ip=>{saddr=>$src}}) if (defined($src));

my @dstmac=split('\.',$dst);
if ($dstmac[0] >= 224 and $dstmac[0] <= 239){
  usage if (!defined($if));

  if($dstmac[1]>127){
    $dstmac[1]-=128; 
  }
  my $mac=sprintf("01:00:5e:%02x:%02x:%02x",$dstmac[1],$dstmac[2],$dstmac[3]);

  $a->ethnew($if,dest=>$mac);
}

$count--;
if ($count>0){
  for (1..$count){
    print localtime(time())." sending packet dst:$dst rp:$rp\n";
    $a->send();
    sleep $sleep;
  }
}

print localtime(time())." sending packet dst:$dst rp:$rp\n";
$a->send();
