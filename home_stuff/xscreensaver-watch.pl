#!/usr/bin/perl

use strict;
use warnings;
use integer;
use POSIX;

$|=1;
my $blanked = 0;
print "[ ] started = ",POSIX::asctime((localtime(time)));
open (IN, "xscreensaver-command -watch |");
while (<IN>) {
  if (m/^(BLANK|LOCK)/) {
    if (!$blanked) {
      print "[-] locked = ",POSIX::asctime((localtime(time)));
      system "killall synergys";
      system "amixer -q set Master mute";
      system "xset dpms force suspend";
      $blanked = 1;
    }
  } elsif (m/^UNBLANK/) {
    print "[+] unlocked = ",POSIX::asctime((localtime(time)));
    system "amixer -q set Master unmute";
    system "synergys --daemon -a 3.255.255.1:24800 &";
    $blanked = 0;
  }
}
