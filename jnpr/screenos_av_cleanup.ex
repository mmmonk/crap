#!/usr/bin/expect

;# $Id:$

set send_slow {10 .01}
set timeout 60

set username "netscreen"
set password "netscreen"


if { $argc < 1 } {
  puts "\nUsage: $argv0 hosts_list_file.txt\n"
  exit
} 


match_max 50000000

set filelist [lindex $argv 0]
set fp [open $filelist r]
while { [gets $fp host] >=0} {

  set error 0

  spawn ssh -o "LogLevel ERROR" -o "TCPKeepAlive no" $username@$host
 

  expect timeout {
    send_user " connection timeout\n"
    break
  } eof {
    send_user " connection interrupted\n"
    break
  } "Permission denied, please try again." {
    send_user " wrong credentials\n"
    break
  } "assword:" {
    send -s "$password\r"
    exp_continue
  } "login:" {
    send -s "$username\r"  
    exp_continue
  } "Are you sure you want to continue connecting" {
    send -s "yes\r"
    exp_continue
  } "*-> " {
    send -s "get av scan-mgr | i \"last result\"\r"
  }

  set result "test"

  expect "*->" {
    regexp {last result: (.+?)$} $expect_out(buffer) match result
    send -s "\r" 
  }



  if { $result != "test" } {

    match_max 50000000

    expect timeout {                                                                                                                                                  send_user " connection timeout\n"
      break
    } eof {
      send_user " connection interrupted\n"
      break
    } "*-> " {
      send -s "exec vfs ls /kav_db\n"
    }

    expect timeout {                                                                                                                                                  send_user " connection timeout\n"
      break
    } eof {
      send_user " connection interrupted\n"
      break
    } "*-> " {
      set data [split $expect_out(buffer) "\n"]
      foreach line $data {
        if { ! [ regexp {( on disk|.+->|exec vfs ls)} $line ] } {  
          regexp {\s*(\S+)\s+} $line devnull filename
          send -s "exec vfs unlink flash:/kav_db/$filename\r"
          expect "*->"
        }
      }
      sleep 20
      send -s "exec av scan-mgr pattern-update\r"
    }

    match_max 2000
  }

  expect timeout {
    send_user " connection timeout\n"
    break
  } eof {
    send_user " done\n"
  } "*-> " {
    send -s "exit\r"
    exp_continue
  } "Configuration modified, save?" {
    send -s "n\r"
    exp_continue
  }

}
close $fp 
