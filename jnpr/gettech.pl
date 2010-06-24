#!/usr/bin/perl

#### <m.lukaszuk@gmail.com>
#### @2010 

use strict;
use warnings;

my $file=shift;

open(GT,$file);
my $gt=join('',<GT>);
close(GT);

# cleaning up the variable
$gt=~s/(\x08|\x0d|--- more ---              )//g;

my $part;

sub getoutput;
sub printerr;

# this sorts the task based on runtime
if (getoutput("get os")==0) {
  my %task;

  my $sorting=0;
  foreach my $line (split /\n/, $part){
    if ($line=~/^\s+\d+\s+/){
      (my $tmp = $line)=~s/^\s+\d+\s+(.{16}?)\s*(.+?\s+){6}(.+?),\s+.*/$1|$3/;
      my @a=split(/\|/,$tmp);
      $task{$a[1]}=$a[0];
      $sorting=1;
    }else{
      if ($sorting==1){
        foreach my $key (sort {$b <=> $a} keys %task){
          foreach my $line (split /\n/, $part){
            print $line."\n" if ($line=~/^\s+\d+\s+/ and $line=~/$task{$key}/);
          }
        }
        $sorting=0;
      }
      print $line."\n";
    }
  }
}

# checking net-pak
# "miss" collumn > 0 
# "full" collumn > 0
if (getoutput("get net-pak")==0) {
  my $err=0;

  my $in1=0;my $in2=0;

  foreach my $line (split /\n/, $part){
    if ($line=~/(^\s+$|^scheduling category)/){
      $in1=0;$in2=0;
    } 
    
    if ($in1==1){
      my $tmp = (split(" ",$line))[7];
      $err=1 if (defined($tmp) and $tmp=~/^\d+$/ and not $tmp == 0);
    }

    if($in2==1){
      (my $tmp = $line)=~s/^.{8}\s+(\d+\s+){4}(\d+).*/$1/;
      $err=1 if ($tmp=~/^\d+$/ and $tmp > 0);
    }

    $in1=1 if ($line=~/name\s+memory\s+total\s+bufsize\s+free\s+max\s+hit\s+miss/i);
    $in2=1 if ($line=~/name\s+max\s+cur\s+write\s+read\s+full\s+delay\s+Applications/i);

    if ($err==0){
      print $line."\n";
    }else{
      printerr($line);
      $err=0;
    }
  }
}

# checking for half-duplex
if (getoutput("get system")==0) {
  my $err=0;
  foreach my $line (split /\n/, $part){
    if ($line=~/half-duplex/){
      $err=1; 
    }

    if ($err==0){
      print $line."\n";
    }else{
      printerr($line);
      $err=0;
    }
  }
}

# checking memory usage
# allocated > 80%
# fragmented > 5%
if (getoutput("get memory")==0) {
  my $err=0;

  foreach my $line (split /\n/, $part){
    if ($line=~/allocated\s+(\d+),\s+left\s+(\d+),\s+frag\s+(\d+)/){
      $err=1 if (($1!=0 and $2!=0) and ($1/($1+$2))*100>80);
      $err=1 if (($1!=0 and $2!=0) and ($3/($1+$2))*100>5);
    }

    if ($err==0){
      print $line."\n";
    }else{
      printerr($line);
      $err=0;
    }
  }
}

# checking chassis
# state of power supplies, fans, battery other then "Good"
# cpu temperature > 90C
# sys temperature > 65C 
if (getoutput("get chassis")==0) {
  my $err=0;
  foreach my $line (split /\n/, $part){
    if ($line=~/(Power Supply|Fan\d? Status|Battery Status)/){
      $err=1 if ((split(" ",$line))[2] ne "Good");
    }

    if ($line=~/CPU Temperature:/){
      (my $temp=$line)=~s/^.+\(\s*(\d+)'C\).*/$1/;
      $err=1 if ($temp>90);
    }

    if ($line=~/System Temperature:/){
      (my $temp=$line)=~s/^.+\(\s*(\d+)'C\).*/$1/;
      $err=1 if ($temp>65);
    }

    if ($err==0){
      print $line."\n";
    }else{
      printerr($line);
      $err=0;
    }
  }
}

# checking self tcp
# tcp checksum error
# tcp unknown port
# tcp no more socket
# tcp syn pak error
# tcp socket full drop count
# tcp ooo segs
# tcp ooo segs drop count
# are >0
if (getoutput("get tcp")==0) {
  my $err=0;
  my %ignore = ("tcpuserauth" => 1,"tcphttpping" => 1);

  foreach my $line (split /\n/, $part){
    if ($line=~/^tcp /){
      my @tmp=split(',',$line);
      foreach my $tmp1 (@tmp){
        if ($tmp1=~/(.+)\s+(\d+).*/){
          my $cname=$1;
          my $cval=$2;

          $cname=~s/\s+//g;

          $err=1 if ($cval>0 and not exists($ignore{$cname}));
        } 
      }
    }

    if ($err==0){
      print $line."\n";
    }else{
      printerr($line);
      $err=0;
    }
  }
}

# all the counters except those in the %ignore >0
if (getoutput("get counter")==0) {
  my $err=0;

  my %ignore = ( 
    "inbytes" => 1, "outbytes" => 1,
    "inucast" => 1, "outucast" => 1,
    "inmcast" => 1, "outmcast" => 1,
    "inbcast" => 1, "outbcast" => 1,
    "invlan" => 1, "outvlan" => 1,
    "inpermit" => 1, "outpermit" => 1,
    "inpackets" => 1, "outpackets" => 1,
    "connections" => 1, "inicmp" => 1,
    "policydeny" => 1
  );

  foreach my $line (split /\n/, $part){
    if ($line=~/\|/){
      my @tmp=split('\|',$line);
      foreach my $counter (@tmp){
        if ($counter=~/(.+)\s+(\d+).*/){
          my $cname=$1;
          my $cval=$2;

          $cname=~s/\s+//g; 
          $err = 1 if ($cval > 0 and not exists($ignore{$cname}));
        }
      }
    }

    if ($err==0){
      print $line."\n";
    }else{
      printerr($line);
      $err=0;
    }
  }
}



###################################### small stuff

sub getoutput{
  my $text=shift;

  if ($gt=~/$text/){
    
    print "\n$text";
   
    ($part=$gt)=~s/.*?$text(.+?)get.*/$1/s;
  
    return 0;
  }else{
    return 1;
  }
}

sub printerr{
  my $text=shift;

  print "\e[0;30;41m$text\e[0;0;0m\n";
}
