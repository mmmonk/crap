#!/usr/bin/expect

;# $Id$

;# Author: <m.lukaszuk@gmail.com>
;# License: GPLv3

;# NO WARRANTY
;# 
;# THE PROGRAM IS  DISTRIBUTED IN THE HOPE THAT  IT WILL  BE USEFUL, BUT  WITHOUT ANY WARRANTY. IT 
;# IS PROVIDED  "AS IS" WITHOUT WARRANTY OF ANY  KIND, EITHER EXPRESSED OR IMPLIED, INCLUDING, BUT 
;# NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE. 
;# THE ENTIRE RISK AS TO THE QUALITY AND PERFORMANCE OF THE PROGRAM IS WITH YOU. SHOULD THE 
;# PROGRAM PROVE DEFECTIVE, YOU ASSUME THE COST OF ALL NECESSARY SERVICING, REPAIR OR CORRECTION.
;# 
;# IN NO EVENT UNLESS REQUIRED BY APPLICABLE LAW THE AUTHOR WILL BE LIABLE TO YOU FOR DAMAGES, 
;# INCLUDING ANY GENERAL, SPECIAL, INCIDENTAL OR CONSEQUENTIAL DAMAGES ARISING OUT OF THE USE OR 
;# INABILITY TO USE THE PROGRAM (INCLUDING BUT NOT LIMITED TO LOSS OF DATA OR DATA BEING RENDERED 
;# INACCURATE OR LOSSES SUSTAINED BY YOU OR THIRD PARTIES OR A FAILURE OF THE PROGRAM TO OPERATE 
;# WITH ANY OTHER PROGRAMS), EVEN IF THE AUTHOR HAS BEEN ADVISED OF THE POSSIBILITY OF SUCH DAMAGES. 

set send_slow {10 .01}
set timeout 60

;# default username and password
set username "netscreen"
set password "netscreen"

if { $argc < 1 } {
  puts "\nUsage: $argv0 hosts_list_file.txt <password> <username>\n"
  exit
} 

if { $argc > 1 } {
  set password [lindex $argv 1]
  if { $argc > 2 } {
    set username [lindex $argv 2]
  }
}

;# to enable debug please change this value below to 1
log_user 0

set filelist [lindex $argv 0]
set fp [open $filelist r]
while { [gets $fp host] >=0} {

  set error 0

  send_user "\[+\] $host - "


  spawn ssh -oControlMaster=auto -oLoglevel=ERROR -oTCPkeepalive=no $username@$host
 
  expect timeout {
    send_user "connection timeout\n"
    close
    continue 
  } eof {
    send_user "connection interrupted\n"
    continue
  } "Permission denied, please try again." {
    send_user " wrong credentials\n"
    continue 
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

  if { [regexp "signature files copy to disk failed" $result] } {

    match_max 50000000

    send_user " freeing space"

    expect timeout {
      send_user "connection timeout\n"
      close
      continue
    } eof {
      send_user "connection interrupted\n"
      continue
    } "*-> " {
      send -s "exec vfs ls /kav_db\n"
    }

    expect timeout {
      send_user "connection timeout\n"
      close
      continue
    } eof {
      send_user "connection interrupted\n"
      continue
    } "*-> " {
      set data [split $expect_out(buffer) "\n"]
      foreach line $data {
        if { ! [ regexp {( on disk|.+->|exec vfs ls)} $line ] } {  
          regexp {\s*(\S+)\s+} $line devnull filename
          send -s "exec vfs unlink flash:/kav_db/$filename\r"
          expect "*->"
        }
      }
      sleep 5
      send -s "exec av scan-mgr pattern-update\r"
    }

    match_max 2000
  }

  expect timeout {
    send_user "connection timeout\n"
    close
    continue
  } eof {
    send_user "done\n"
  } "*-> " {
    send -s "exit\r"
    exp_continue
  } "Configuration modified, save?" {
    send -s "n\r"
    exp_continue
  }

}
close $fp 
