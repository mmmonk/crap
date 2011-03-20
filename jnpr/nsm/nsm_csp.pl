#!/usr/bin/perl

# $Id$ 

use strict;
use warnings;

my %nsm;
#loading NSM naming file
open(FD,"/home/www/perl/nsm_naming.txt") or die "can't load file\n";
while(<FD>){
  next unless ($_);
  chomp;
  my ($a,$b)=split(" ");
  $nsm{$a}=$b;                                                                                                                                                            }
close(FD);

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
  next unless ($nsmver=~/^LGB/ and -d $homedir."/".$nsmver);
  if (exists($params{'q'}) and $params{'q'} ne ""){
    if (exists($params{'m'}) and $params{'m'}==1){
      push(@nsmverl,$nsmver) if ($nsmver=~/^$params{'q'}$/i);
    }else {
      push(@nsmverl,$nsmver) if ($nsmver=~/$params{'q'}/i);
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
          $all{"$nsmver#$currentpr"}=" " unless (exists($params{'prt'}) and $params{'prt'} ne "");
          next;
        }
        next if (exists($params{'prn'}) and $params{'prn'} ne "" and $currentpr!~/$params{'prn'}/);
        next if (exists($params{'prt'}) and $params{'prt'} ne "" and $f!~/$params{'prt'}/i);
        $all{"$nsmver#$currentpr"}=$f;
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
<h1 align=\"center\"><a href=\"?\">$pagetitle</a></h1>\n";

print "<table width=\"90%\" border=\"0\" align=\"center\">\
<form method=\"get\" enctype=\"multipart/form-data\">\
<tr><td align=\"right\">NSM version:</td><td><input type=\"text\" name=\"q\" value=\"";
print $params{'q'} if (exists($params{'q'}));
print "\"/></td></tr>\
<tr><td align=\"right\">PR number:</td><td><input type=\"text\" name=\"prn\" value=\"";
print $params{'prn'} if (exists($params{'prt'}));
print "\"/></td></tr>\
<tr><td align=\"right\">PR title:</td><td><input type=\"text\" name=\"prt\" value=\"";
print $params{'prt'} if (exists($params{'prt'}));
print "\"/> this is case insensitive</td></tr>\
<tr><td>&nbsp;</td><td><input type=\"submit\" value=\"search\"/></td></tr>\
<tr><td>&nbsp;</td><td><a href=\"?q=LGB13&prt=srx\">example search for all PRs titles with \"SRX\" in them on NSM versions with \"LGB13\"</a></td></tr>";
if (exists($params{'q'}) and $params{'q'} ne ""){
  print "<tr><td>&nbsp;</td><td><a href=\"https://gnats.juniper.net/web/default/do-query?adv=0&OPT_product=EXACT&product=nsm&target=".$params{'q'}."&OPT_target=MATCH&csv=0&columns=synopsis%2Creported-in%2Csubmitter-id%2Cproduct%2Ccategory%2Cseverity%2Cpriority%2Cblocker%2Cplanned-release%2Cstate%2Cresponsible%2Coriginator%2Carrival-date%2Ctarget&op=%26\">gnats search for PRs with target release matching ".$params{'q'}."</a></td></tr>\n";
}
print "</form>\
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
  my $mainver="";
  if ($nsmver=~/(LGB\d+z\d+)(.*)/){
    $mainver=$nsm{$1} if (exists($nsm{$1}));
  }
  print "<tr><td NOWRAP><a href=\"?q=$nsmver&m=1\">$nsmver ($mainver)</a></td><td><a href=\"https://gnats.juniper.net/web/default/$pr\">$pr</a></td><td>".$all{$nsmpr}."</td></tr>\n";
}

print "</table><p align=\"center\"><a href=\"mailto:mlukaszuk\@juniper.net\">complains/ideas/money</a></p></body></html>\n";

