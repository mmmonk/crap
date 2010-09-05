#!/usr/bin/perl 

# $Id$

use strict;
use warnings;
use integer;

use Expect;
use POSIX qw(:termios_h);

# max children running
my $maxkids=64;
# timeout for the spawn in expect process
my $timeout=30;

my $username="netscreen";
my $password="netscreen";

my $hostsfile=shift;
my $cmdsfile=shift;
my @cmds;

# reading commands for per host execution
open(FD,$cmdsfile) or die "$!\n";
while(<FD>){
  next if (/^\s+$/);
  chomp;
  push(@cmds,$_);  
}
close(FD);


# reading file with hosts to connect to
open(FD,$hostsfile) or die "$!\n";

$|=1;
my $kids=0; 

while (<FD>){

  next unless ($_);

  $kids++;

  if (fork == 0){
    chomp;
    my $host=$_;
 
    my $exp = Expect->new();

    $exp = Expect->spawn("ssh -t -l $username $host 2>&1");

    # no output from the expect session
    $exp->log_user(0);

    # logging process
    $exp->expect($timeout,
      ['eof' => sub { print "$host - connection interrupted\n";
                      exit;}],
      ['timeout' => sub { print "$host - connection timeout\n";
                          exit;}],
      [qr/you sure you want to continue connecting/ => sub {  my $e=shift;
                                                              $e->send("yes\n");
                                                              exp_continue;}],
      [qr/RSA modulus too small: \d+ < minimum 768 bits/ => sub {print "$host - too small RSA key.\n";
                                                                exit;}],
      [qr/Permission denied, please try again/ => sub { print "$host - wrong credentials\n";
                                                        exit;}],
      [qr/login:/ => sub {  my $e=shift;
                            $e->send("$username\r");
                            exp_continue;}],
      [qr/assword:/ => sub {  my $e=shift;
                              $e->send("$password\r");
                              exp_continue;}],
      [qr/.*?-> / => sub {  my $e=shift;
                          $e->send("\r");}]
    );


    # running commands
    foreach my $cmd (@cmds){
      $exp->expect($timeout,
        ['eof' => sub { print "$host - connection interrupted\n";
                        exit;}],
        ['timeout' => sub { print "$host - connection timeout\n";
                            exit;}],
        [qr/--- more ---/ => sub {  my $e=shift;
                                    $e->send(" ");
                                    exp_continue;}],
        [qr/.*?-> / => sub {  my $e=shift;
                              $e->send("$cmd\r");}]
      ); 
    }
    
    # exiting
    $exp->expect($timeout,
      ['eof' => sub { print "$host - done\n";
                      exit;}],
      ['timeout' => sub { print "$host - connection timeout\n";
                          exit;}],
      [qr/--- more ---/ => sub {  my $e=shift;
                                  $e->send(" ");
                                  exp_continue;}],
      [qr/.*?-> / => sub {  my $e=shift;
                            $e->send("exit\r");
                            exp_continue;}],
      [qr/Configuration modified, save\?/ => sub {  my $e=shift;
                                                    $e->send("n");
                                                    exp_continue;}]
    ); 
    
    exit;

  }else{

    # birth control ;) 
    # making sure that we don't have too many kids
    if ($kids>=$maxkids){
      my $pid=wait();
      $kids--;
    }
  }
}
close(FD);

# waiting before exit, for all kids running around 
while(wait>0){ }
