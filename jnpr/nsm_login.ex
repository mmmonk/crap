#!/usr/bin/expect -f

;# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>

set send_slow {10 .01}
set timeout 60

if { $argc == 1} {
  set host [lindex $argv 0]
} else {
  exit;
}

set user "root"
set pass "netscreen"

spawn ssh $user@$host

proc talking {} {
  global pass
  interact {
    \001l { send "$pass\r" }
    \004  { 
      send_user "\n"
      exit 
    } 
  }
}

expect timeout {
  send_user "connection timeout\n"
  exit
} eof {
  send_user "got eof\n"
  exit
} "Permission denied, please try again." {
  set user "admin"
  close
  spawn ssh $user@$host
} "assword:" {
  send -s "$pass\r"
  exp_continue
} "*# " {
  talking
}

if { $user == "admin" } {
  expect timeout {
    send_user "connection timeout\n"
    exit
  } eof {
    send_user "got eof\n"
    exit
  } "Permission denied, please try again." {
    send_user "can't connect\n"
  } "assword:" {
    send -s "$pass\r"
    exp_continue
  } "Run NSMXPress system setup" {
    send -s "n"
    exp_continue
  } "*$ " {
    send -s "sudo su -\r"
    exp_continue
  } "*# " {
    send -s "unset TMOUT\r"
    talking
  }
}


