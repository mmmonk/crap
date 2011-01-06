#!/usr/bin/perl

use strict;
use warnings;

# NSM version sorting
sub sorting {
  my (@aa, @bb);
  ($aa[0] = $a ) =~ s/LGB(\d+).*/$1/;
  ($aa[1] = $a ) =~ s/LGB\d+\D+(\d+).*/$1/;
  ($aa[2] = $a ) =~ s/LGB\d+\D+\d+(\D+).*/$1/;
  ($aa[3] = $a ) =~ s/LGB\d+\D+\d+\D+(\d+).*/$1/;
  ($bb[0] = $b ) =~ s/LGB(\d+).*/$1/;
  ($bb[1] = $b ) =~ s/LGB\d+\D+(\d+).*/$1/;
  ($bb[2] = $b ) =~ s/LGB\d+\D+\d+(\D+).*/$1/;
  ($bb[3] = $b ) =~ s/LGB\d+\D+\d+\D+(\d+).*/$1/;
   
  $bb[0] <=> $aa[0] || $bb[1] <=> $aa[1] || $bb[2] cmp $aa[2] || $bb[3] <=> $aa[3];
}

my $homedir="/home/case/store/jj/nsmdiff_and_stuff";

# getting GET values
my %params=map{my($name,$value)=split/\=/;$name => $value} map{split /\&/} $ENV{"QUERY_STRING"};

### the real work is done here
my @nsmverl=();
opendir(DIR,$homedir);
while(my $nsmver=readdir(DIR)){
  next unless ($nsmver=~/^LGB/);
  if (exists($params{'q'}) and $params{'q'} ne ""){
    if (exists($params{'m'}) and $params{'m'}==1){
      push(@nsmverl,$nsmver) if ($nsmver=~/^$params{'q'}$/);
    }else {
      push(@nsmverl,$nsmver) if ($nsmver=~/$params{'q'}/);
    }
  } else {
    push(@nsmverl,$nsmver);
  }
}
closedir(DIR);

my %all;
foreach my $nsmver (@nsmverl) {
  opendir(DIFF,$homedir."/".$nsmver);
  while(my $diff=readdir(DIFF)){
    next unless ($diff=~/filediff/);
    my $currentpr="";
    open(FD,$homedir."/".$nsmver."/".$diff);
    while(<FD>){
      chomp;
      if (/^<\s+(Bug:|\/B:|Title:)\s*(.+?)$/){
        my $f=$2;
        if (/^<\s+(Bug:|\/B:)/) {
          next if ($f=~/new/i);
          $f=~s/-.+?//;
          $currentpr=$f;
          next if (exists($all{"$nsmver#$currentpr"}));
          $all{"$nsmver#$currentpr"}=" ";
          next;
        }
        next unless (exists($all{"$nsmver#$currentpr"}) and $all{"$nsmver#$currentpr"} eq " ");
        if (exists($params{'prt'}) and $params{'prt'} ne ""){
          $all{"$nsmver#$currentpr"}=$f if ($f=~/$params{'prt'}/i);
        } else {
          $all{"$nsmver#$currentpr"}=$f;
        }
      }
    }
    close(FD);
  }
  closedir(DIFF);
}

my $pagetitle="patch list with fixes for NSM";

# we start output here
print "Content-type: text/html\n\n\
<html>\
<head>\
<title>$pagetitle</title>\
</head>\
<body> 
<h1 align=\"center\"><a href=\"?\">$pagetitle</a></h1>\
<table width=\"90%\" border=\"0\" align=\"center\">\
<form method=\"get\" enctype=\"text/plain\">\
<tr><td align=\"right\">NSM version:</td><td><input type=\"text\" name=\"q\" value=\"";
print $params{'q'} if (exists($params{'q'}));
print "\"/></td></tr>\
<tr><td align=\"right\">PR title:</td><td><input type=\"text\" name=\"prt\" value=\"";
print $params{'prt'} if (exists($params{'prt'}));
print "\"/></td></tr>\
<tr><td>&nbsp;</td><td><input type=\"submit\" value=\"search\"/></td></tr>\
</form>\
</table></br>";

my $link="?";
#foreach my $key (keys %params){
#  $link.=$key."=".$params{$key}."&";
#}

print "</br><table width=\"90%\" border=\"1\" frame=\"border\" align=\"center\">\
<tr><th><a href=\"$link\">patch</a></th>\
<th><a href=\"$link\">PR#</a></th>\
<th><a href=\"$link\">PR title</a></th></tr>\n";

foreach my $nsmpr (sort sorting keys %all){
  my ($nsmver,$pr) = split/#/,$nsmpr;
  print "<tr><td><a href=\"?q=$nsmver&m=1\">$nsmver</a></td><td><a href=\"https://gnats.juniper.net/web/default/$pr\">$pr</a></td><td>".$all{$nsmpr}."</td></tr>\n";
}

print "</table></body></html>\n";

