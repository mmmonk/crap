#!/usr/bin/expect -f

# $Id$

set send_slow {5 .02}
set timeout 60
set user "lab"
set pass "lab123"
set pattern "User lab logged in"


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

log_file "~/check_parity-$filetime.log"

proc counterrors {pattern logs} {
  set errorcount 0
  foreach line [split $logs "\n"] {
    if { [regexp "/var/log/messages" $line] } {
      continue
    }
    if { [regexp $pattern $line] } {
      incr errorcount 1
    }
  }
  return $errorcount
}

set file [lindex $argv 0]
set fp [open $file r]
set file_data [read $fp]
close $fp

foreach host [split $file_data "\n"] {

  set errorperhost 0

  if { $host != "" } {
    
    if { [regexp ":" $host] } {
      regexp {:(\S+)} $host match pass
      regexp {(\S+):} $host match host
    }

    if { [regexp "@" $host] } {
      regexp {(\S+?)@} $host match user
      regexp {@(\S+)} $host match host
    }
    
    spawn telnet $host

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
    } "*> " {
      send -s "\r"
    }

    set master [regexp -inline -- {master:\d+} $expect_out(buffer)]
    set master [regexp -inline -- {\d+} $master]

    set errorpermember 0

    expect timeout {
      send_user "\n$host: CONNECTION ERROR - connection timeout\n"
      break 
    } eof {
      send_user "\n$host: CONNECTION ERROR - got eof\n"
      break
    } "*> " {
      send -s "start shell\r"
      exp_continue
    } "*% " {
      send -s "cat /var/log/messages | grep '$pattern'\r"
    }
    set errorpermember [ counterrors $pattern $expect_out(buffer)]
    expect "*% " {send -s "zcat /var/log/messages*gz | grep '$pattern'\r"}
    set moreerror [ counterrors $pattern $expect_out(buffer)]
    set errorpermember [expr $errorpermember+$moreerror]
    set errorperhost [expr $errorperhost+$errorpermember]
    send_user "\n#### $host:$master has $errorpermember errors ####\n"
    expect "*% " {send -s "exit\r"}


    set errorpermember 0
    set done 0
    for { set x 0 } { $x<=9 } { incr x } {
      if { $x != $master } {
        expect timeout {
          send_user "\n$host: CONNECTION ERROR - connection timeout\n"
          break
        } eof {
          send_user "\n$host: CONNECTION ERROR - got eof\n"
          break
        } "*> " { 
          send -s "request session member $x\r"
        }
        
        expect timeout {
          send_user "\n$host: CONNECTION ERROR - connection timeout\n"
          break
        } eof {
          send_user "\n$host: CONNECTION ERROR - got eof\n"
          break
        } "assword: " {
          send -s "$pass\r"
          exp_continue
        } "No route to host" {
          continue
        } "*> " {
          send -s "start shell\r"
          exp_continue
        } "*% " {
          send -s "cat /var/log/messages | grep '$pattern'\r"
        }
        set errorpermember [ counterrors $pattern $expect_out(buffer)]
        expect "*% " {send -s "zcat /var/log/messages*gz | grep '$pattern'\r"}
        set moreerror [ counterrors $pattern $expect_out(buffer)]
        set errorpermember [expr $errorpermember+$moreerror]
        set errorperhost [expr $errorperhost+$errorpermember]
        send_user "\n#### $host:$x has $errorpermember errors ####\n"

        expect "*% " {send -s "exit\r"}
      }
    }
    send_user "\n#### $host in total has $errorperhost errors ####\n"
    expect "*> " { send -s "exit\r"}
  }
}
