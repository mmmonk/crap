#!/usr/bin/expect -f

;# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>

set send_slow {10 .01}
set timeout 60

if { $argc == 0 } {
  exit
} else {
  set host [lindex $argv 0]
  set user "root"
  set pass "netscreen"
  if { $argc > 1 } {
    set user [lindex $argv 1]
    if { $argc > 2 } {
      set pass [lindex $argv 2]
    }
  }
}

spawn ssh $user@$host

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
set filetime [ timestamp -format "%Y%m%d_%H%M%S"]

send_user "\033]2;$host $filetime\007"

expect timeout {
  send_user "connection timeout\n"
  exit
} eof {
  send_user "got eof\n"
  exit
} "Permission denied, please try again." {
  send_user "wrong credentials\n"
  exit
} "Are you sure you want to continue connecting (yes/no)?" {
  send -s "yes\r"
  exp_continue
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
}

expect "*# " {
  log_file "/home/case/store/work/_archives_worklogs/$host-$filetime.log"
  send_log "\n---------- log start at $time ----------\n"

  interact {
    \001l { send "$pass\r" }
  }
}

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
send_log "\n---------- log close at $time ----------\n"
log_file
exec /bin/bzip2 /home/case/store/work/_archives_worklogs/$host-$filetime.log
exit

