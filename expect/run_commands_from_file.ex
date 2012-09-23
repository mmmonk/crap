#!/usr/bin/expect -f

# $Id: 20120921$
# $Date: 2012-09-21 19:49:18$
# $Author: Marek Lukaszuk$

set send_slow {10 .01}
set timeout 90

if { $argc == 0 } {
  puts "
Usage: $argv0 host filename <count>

"
  exit
} else {
  set host [lindex $argv 0]
  set user "root"
  set pass "lab123"
  set filename [lindex $argv 1]
  set count 1
  if { $argc > 2 } {
    set count [lindex $argv 2]
  }
}

spawn telnet $host-con

send -s "\r"

expect timeout {
  send_user "connection timeout\n"
  exit
} eof {
  send_user "got eof\n"
  exit
} "ogin incorrect" {
  send_user "wrong credentials\n"
  exit
} "ogin:" {
  send -s "$user\r"
  exp_continue
} "assword:" {
  send -s "$pass\r"
  exp_continue
} -re ".*% " {
  send -s "cli\r"
  exp_continue
} -re ".*# " {
  send -s "commit and-quit\r"
  exp_continue
} -re ".*> " {
  send -s "\r"
}

set send_slow {5 .01}

set fp [open $filename r]
set file_data [read $fp]
close $fp
set data [split $file_data "\n"]
for { set i 0 } { $i < $count } { incr i } {
  foreach line $data {
    expect -re ".*(>|#|%) " {
      send -s "$line\r"
    }
    sleep 1
  }
  sleep 2
}
