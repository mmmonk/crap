#!/usr/bin/perl 

# $Id$

use strict;
use warnings;
use integer;

use Expect;
use POSIX qw(:termios_h);

## max children running around
my $maxkids = 64;

## timeout for the spawn in expect process
my $timeout = 30;

## default username and password
my $username = "netscreen";
my $password = "netscreen";

## prompt on the device
my $prompt = "\\S+-> ";

my $hostsfile = shift;
my $cmdsfile = shift;

die "Usage:
$0 <file_with_list_of_hosts> <file_with_lists_of_commands>

Host file example:
172.30.72.87
user1\@password2:172.30.72.88
telnet://junos\@qwerty:172.30.72.89

Commands file example:
get clock
get sys
get tech\n\n" unless ($cmdsfile);


######## fun begins from here 

sub timer;

my @cmds;

## reading commands into an array for per host execution
open(FD,$cmdsfile) or die "$!\n";
while(<FD>){
  next unless ($_);
  chomp;
  push(@cmds,$_);  
}
close(FD);


## reading file with hosts to connect to
open(FD,$hostsfile) or die "$!\n";

$| = 1;
my $kids = 0; 

my $starttime = timer();

while (<FD>){

  next unless ($_);

  $kids++;

  # making kids 
  if (fork == 0){

    ######## this is inside the kid
    chomp;

    my $host = $_;

    if (/^(.+?\:\/\/)?(.+?)\@(.+?)\:(.+?)$/) {
      $username = $2;
      $password = $3;
      $host = $4;
    }

    my $exp = Expect->new();

    $exp->raw_pty(1);
  
    if (/^telnet\:\/\//i){
      $exp->spawn("telnet $host");
    } else {
      $exp->spawn("ssh -t -oControlMaster=auto -oLoglevel=ERROR -oTCPkeepalive=no -l $username $host");
    }

    ### no output to stdout from the expect session
    $exp->log_user(0);

    ### logging everything to file
    $exp->log_file($starttime."_".$host.".log");

    ##### login into device
    $exp->expect($timeout,
      ['eof' => sub { print "$host - problem with connecting to the device\n";
                      exit;}],
      ['timeout' => sub { print "$host - connection timeout\n";
                          exit;}],
      [qr/you sure you want to continue connecting/ => sub {  my $e=shift;
                                                              $e->send("yes\n");
                                                              exp_continue;}],
      [qr/RSA modulus too small: \d+ < minimum 768 bits/ => sub { print "$host - too small RSA key.\n";
                                                                  exit;}],
      [qr/(Permission denied, please try again|Login failed)/ => sub {  print "$host - wrong credentials\n";
                                                                        exit;}],
      [qr/(login:|user)/i => sub {  my $e=shift;
                                    $e->send("$username\r");
                                    exp_continue;}],
      [qr/assword:/ => sub {  my $e=shift;
                              $e->send("$password\r");
                              exp_continue;}],
      [qr/$prompt/ => sub { my $e=shift;
                            $e->send("\r");}]
    );

    ##### running commands
    foreach my $cmd (@cmds){
      $exp->expect($timeout,
        ['eof' => sub { print "$host - connection interrupted\n";
                        exit;}],
        ['timeout' => sub { print "$host - connection timeout\n";
                            exit;}],
        [qr/--- more ---/ => sub {  my $e=shift;
                                    $e->send(" ");
                                    exp_continue;}],
        [qr/$prompt/ => sub { my $e=shift;
                              $e->send("$cmd\r");}]
      ); 
    }
    
    ##### logout from the device - if we survived that long ;) 
    $exp->expect($timeout,
      ['eof' => sub { print "$host - done\n";
                      exit;}],
      ['timeout' => sub { print "$host - connection timeout\n";
                          exit;}],
      [qr/--- more ---/ => sub {  my $e=shift;
                                  $e->send(" ");
                                  exp_continue;}],
      [qr/$prompt/ => sub { my $e=shift;
                            $e->send("exit\r");
                            exp_continue;}],
      [qr/Configuration modified, save\?/ => sub {  my $e=shift;
                                                    $e->send("n");
                                                    exp_continue;}]
    ); 
    
    ######## this is the end of the kid
    exit;

  }else{

    ## birth control ;) 
    ## making sure that we don't have too many kids
    if ($kids >= $maxkids){
      wait();
      $kids--;
    }
  }
}
close(FD);

### waiting before exit for all the kids running around 
while(wait>0){ }

######### end of main

## this is for pretty printing time ;)
sub timer {
  my ($sec, $min, $hour, $mday, $mon, $year);
  ( $sec, $min, $hour, $mday, $mon, $year, undef, undef, undef ) = localtime(time);
  $year += 1900;
  $mon  += 1;
  $hour = "0$hour" if $hour < 10;
  $mday = "0$mday" if $mday < 10;
  $mon  = "0$mon"  if $mon < 10;
  $min  = "0$min"  if $min < 10;
  $sec  = "0$sec"  if $sec < 10;
  return $year . "-" . $mon . "-" . $mday . "_" . $hour . "-" . $min . "-" . $sec;
}
