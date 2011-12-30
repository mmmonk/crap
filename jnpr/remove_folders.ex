#!/usr/bin/expect -f

# $Id$

set send_slow {5 .02}
set timeout 60

# default user and pass
set defuser "lab"
set defpass "lab123"


if { $argc == 0 } {
  puts "
Usage: $argv0 filename

hosts definitions inside the file should be in a format:
<user>@host<:pass>

examples:
127.0.0.1
user1@127.0.0.2
user2@127.0.0.3:pass2

if the user or pass are not specified the default values are used.
"
  exit
} 

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
set filetime [ timestamp -format "%Y%m%d_%H%M%S"]

log_file "~/remove_folders-$filetime.log"

set file [lindex $argv 0]
set fp [open $file r]
set file_data [read $fp]
close $fp

foreach host [split $file_data "\n"] {

  set user $defuser
  set pass $defpass

  if { $host != "" } {
    
    if { [regexp ":" $host] } {
      regexp {:(\S+)} $host match pass
      regexp {(\S+):} $host match host
    }

    if { [regexp "@" $host] } {
      regexp {(\S+?)@} $host match user
      regexp {@(\S+)} $host match host
    }
    
    spawn ssh $user@$host

    expect timeout {
      send_user "\n$host: CONNECTION ERROR - connection timeout\n"
      continue
    } eof {
      send_user "\n$host: CONNECTION ERROR - got eof\n"
      continue
    } "Login incorrect" {
      send_user "\n$host: CONNECTION ERROR - wrong credentials\n"
      continue
    } "Permission denied, please try again." {
      send_user "\n$host: CONNECTION ERROR - wrong credentials\n"
      continue 
    } "Are you sure you want to continue connecting (yes/no)?" {
      send -s "yes\r"
      exp_continue
    } "ogin:" {
      send -s "$user\r"
      exp_continue
    } "assword:" {
      send -s "$pass\r"
      exp_continue
    } "*% " {
      send -s "cli\r"
      exp_continue
    } "*> " {
      send -s "\r"
    }

    expect timeout {
      send_user "\n$host: CONNECTION ERROR - connection timeout before running: file delete /cf/var/db/idpd/sec-download/*\n"
      break 
    } eof {
      send_user "\n$host: CONNECTION ERROR - got eof before running: file delete /cf/var/db/idpd/sec-download/*\n"
      break
    } "*> " {
      send -s "file list /cf/var/db/idpd/sec-download/*\r"
    }
    
    expect timeout {
      send_user "\n$host: CONNECTION ERROR - connection timeout before running: file delete /cf/var/db/idpd/nsm-download/*\n"
      break 
    } eof {
      send_user "\n$host: CONNECTION ERROR - got eof before running: file delete /cf/var/db/idpd/nsm-download/*\n"
      break
    } "*> " {
      send -s "file list /cf/var/db/idpd/nsm-download/*\r"
    }
    
    expect "*> " { 
      send -s "logout\r"
      send_user "\n\n"  
    }
  }
}
