#!/usr/bin/perl

# $Id$

use strict;
use integer;
use warnings;
use Socket;
use Expect;

my $nsmver=shift;
my $nsmserv=lc(shift);
my $user="admin";
my $pass="netscreen";
$nsmver=~s/lgb/LGB/;

die "usage: $0 nsmver nsmserv\n" unless ($nsmserv);

my %conf;
sub loadconf {
  open(CONF,"/home/case/.nsmauth.conf") or die "$!\n";
  while(<CONF>){
    chomp;
    my @a=split('=');
    $conf{$a[0]}=$a[1];
  }
  close(CONF);
}

# easy way of making sure that everything works while sending commands
sub sendcmd {
  my $expect=shift;
  my $ok=shift;
  my $cmd=shift;
  my $timeout=shift || 600;
  if ($ok==1){
    $ok=0;
    $cmd="$cmd && echo SOFAROK";
    $expect->expect($timeout,
      [ qr/SOFAROK/, sub {$ok=1;exp_continue}],
      [ qr/\# /, sub { if ($ok==0) {$cmd="";};my $e=shift;$e->send("$cmd\n") }]
    );
    return $ok;
  }
}

# loading a table that connects LGB versions to years
my %nsm;
open(FD,"/home/www/perl/nsm_naming.txt") or die "can't load file\n";
while(<FD>){
  next unless ($_);
  chomp;
  my ($a,$b)=split(" ");
  $nsm{$a}=$b;
}
close(FD);

die "Not a knonw NSM version\n" unless ($nsmver=~/LGB\d+/i or $nsmver=~/^20\d\d\.\dr\d$/);

my $nsmip="";
if ($nsmserv=~/^(\d+\.){3}\d+$/){
  $nsmip=$nsmserv;
}else{
  $nsmip=join(".",unpack("C4",(gethostbyname($nsmserv))[4]));
}

die "IP address unknown\n" if ($nsmip=~/^\s*$/);

loadconf;

my $nsmmain=$nsmver;
$nsmmain=~s/r\d+// if ($nsmmain=~/^201/);
my $nsmlink="";
my $nsmfile="nsm".$nsmmain."_servers_linux_x86.sh";

if ($nsmver=~/LGB(\d+)z(\d+)(.*)/){
  if (exists($nsm{"LGB$1z$2"})){
    $nsmmain=$nsm{"LGB$1z$2"};
    $nsmfile=$nsmver."_netmgt_1.$1.$2_linux_x86_rpm_bin_opt.sh";
    $nsmmain=~s/r\d+// if ($nsmmain=~/^201/);
    $nsmlink="ftp://".$conf{"nsmdiffuser"}.":".$conf{"nsmdiffpass"}."@".$conf{"nsmdiffftp"}."/".$conf{"nsmdiffremotedir"}."/".$nsmver."/".$nsmfile;
  }else{
    die "can't find mainline version for this nsm version\n";
  }
} 

my $timeout=600;
my $sofarok=1;
my $exp = new Expect;
$exp->log_file("/home/case/nsm_install_$nsmserv.txt", "w");
$exp->spawn("/usr/bin/ssh $user\@$nsmserv") or die "Can't run command\n";
$exp->expect($timeout,
  [ qr/Store key in cache\? \(y\/n\)/, sub { my $e=shift;$e->send("y\n");exp_continue; }],
  [ qr/Are you sure you want to continue connecting \(yes\/no\)\?/, sub { my $e=shift;$e->send("yes\n");exp_continue; }],
  [ qr/password:/i, sub { my $e=shift;$e->send("$pass\n");exp_continue; }],
  [ qr/Run NSMXPress system setup\? \[y\/N\]/, sub { my $e=shift;$e->send("n");exp_continue; }],
  [ qr/\$ /, sub { my $e=shift;$e->send("sudo su -\n");exp_continue; }],
  [ qr/[^\#]+\# /, sub { my $e=shift;$e->send("rm -rf /tmp/netmgt*; cd /var/tmp/ && echo SOFAROK\n") }]
);

if ($nsmver=~/LGB(\d+)z(\d+)(.*)/){
  $sofarok=sendcmd($exp,$sofarok,"(ls $nsmfile || wget -nv -nd -m $nsmlink)");
}
$sofarok=sendcmd($exp,$sofarok,"(ls nsm".$nsmmain."_servers_upgrade_rs.zip || wget -nv -nd -m ftp://172.30.73.133/nsm/nsm".$nsmmain."_servers_upgrade_rs.zip)");
$sofarok=sendcmd($exp,$sofarok,"(ls nsm".$nsmmain."_offline_upgrade.zip || wget -nv -nd -m ftp://172.30.73.133/nsm/nsm".$nsmmain."_offline_upgrade.zip)");
$sofarok=sendcmd($exp,$sofarok,"unzip -o nsm".$nsmmain."_servers_upgrade_rs.zip");
if ($0=~/install\.pl/){
  $sofarok=sendcmd($exp,$sofarok,"rpm -qa | grep netscreen | xargs -r rpm -e ; rm -rf /var/netscreen/*/* /usr/netscreen/*");
}
$sofarok=sendcmd($exp,$sofarok,"chattr +i nsm".$nsmmain."_offline_upgrade.zip; ./upgrade-os.sh $nsmfile offline");
$exp->expect($timeout,
  [ qr/\.\.\.FAILED/,
    sub { my $e=shift;$e->send("\n");}],
  [ qr/--More--/,
    sub { my $e=shift;$e->send(" ");exp_continue;}],
  [ qr/Hit Ctrl-C to abort installation or ENTER to continue/,
    sub { my $e=shift;$e->send("\n");exp_continue;}],
  [ qr/Enter the License File Path>/,
    sub { my $e=shift;$e->send("/var/tmp/lic.txt\n");exp_continue;}],
  [ qr/Hit Ctrl-C to abort upgrade or ENTER to continue/,
    sub { my $e=shift;$e->send("\n");exp_continue;}],
  [ qr/Do you want to do NSM installation with base license\? \(y\/n\).*>/,
    sub { my $e=shift;$e->send("y\r");exp_continue;}],
  [ qr/Enter selection \(1-2\).*>/,
    sub { my $e=shift;$e->send("2\r");exp_continue;}],
  [ qr/Will server\(s\) need to be reconfigured during the refresh\? \(y\/n\).*>/, 
    sub { my $e=shift;$e->send("n\r");exp_continue;}],
  [ qr/Enter selection \(1-3\).*>/, 
    sub { my $e=shift;$e->send("3\r");exp_continue;}],
  [ qr/Enter base directory location for management servers /, 
    sub { my $e=shift;$e->send("\r");exp_continue;}],
  [ qr/Enable FIPS Support\? \(y\/n\).*>/, 
    sub { my $e=shift;$e->send("n\r");exp_continue;}],
  [ qr/Will this machine participate in an HA cluster\? \(y\/n\).*>/, 
    sub { my $e=shift;$e->send("n\r");exp_continue;}],
  [ qr/Enter database log directory location.*>/, 
    sub { my $e=shift;$e->send("\r");exp_continue;}],
  [ qr/Enter the management IP address of this server.*>/, 
    sub { my $e=shift;$e->send("$nsmip\r");exp_continue;}],
  [ qr/Enter the https port for NBI service.*>/, 
    sub { my $e=shift;$e->send("\r");exp_continue;}],
  [ qr/Enter password \(password will not display as you type\)>/, 
    sub { my $e=shift;$e->send("$pass\r");exp_continue;}],
  [ qr/Will a Statistical Report Server be used with this GUI Server\? \(y\/n\).*>/, 
    sub { my $e=shift;$e->send("n\r");exp_continue;}],
  [ qr/UNIX password: /, 
    sub { my $e=shift;$e->send("$pass\r");exp_continue;}],
  [ qr/Will server processes need to be restarted automatically in case of a failure\? \(y\/n\).*>/, 
    sub { my $e=shift;$e->send("y\r");exp_continue;}],
  [ qr/Will this machine require local database backups\? \(y\/n\).*>/, 
    sub { my $e=shift;$e->send("n\r");exp_continue;}],
  [ qr/Enter Postgres DevSvr Db port.*> /, 
    sub { my $e=shift;$e->send("\r");exp_continue;}],
  [ qr/Enter Postgres DevSvr Db super user.*> /, 
    sub { my $e=shift;$e->send("\r");exp_continue;}],
  [ qr/Start server\(s\) when finished\? \(y\/n\).*> /, 
    sub { my $e=shift;$e->send("y\r");exp_continue;}],
  [ qr/Are the above actions correct\? \(y\/n\)> /, 
    sub { my $e=shift;$e->send("y\r");exp_continue;}]
);

$timeout=1200; # 20 minutes
$exp->expect($timeout,
  [ qr/[^\#]+\# /, sub { my $e=shift;$e->send("chattr -i nsm".$nsmmain."_offline_upgrade.zip; exit\n");exp_continue;}],
  [ qr/\$ /, sub { my $e=shift;$e->send("exit\n")} ]
);
$exp->soft_close();

