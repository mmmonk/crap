#!/usr/bin/expect -f

# $Id: 20130410$
# $Date: 2013-04-10 13:11:41$
# $Author: Marek Lukaszuk$

# ver: 20120403

set send_slow {1 .1}
set timeout 90

log_user 1

proc accept {sock addr port} {

  # Setup handler for future communication on client socket
  fileevent $sock readable [list svcHandler $sock]

  # Read client input in lines, disable blocking I/O
  fconfigure $sock -buffering line -blocking 0

  # Send Acceptance string to client
  puts -nonewline $sock "\[+\] Master I'm listening, type your query:\n> "
}

proc  svcHandler {sock} {
  set l [gets $sock]    ;# get the client packet
  if {[eof $sock]} {    ;# client gone or finished
     close $sock        ;# release the servers client channel
  } else {
    doService $sock $l
    puts -nonewline $sock "> "
    flush $sock
  }
}

proc doService {sock msg} {
  set out [ psktest $msg ]
  puts $sock "< $out"
}

proc psktest {tpass} {
  set pass "password"

  expect timeout {
    exp_continue

  } eof {
    exp_continue

  } "Are you sure you want to continue connecting" {
    send -s "yes\r"
    exp_continue

  } "ogin incorrect" {
    send_user "wrong credentials\n"
    exit

  } "assword:" {
    send -s "$pass\r"
    exp_continue

  } " > " {
    send -s "en\r"
    exp_continue

  } "(config) # " {
    send -s "\r"

  } " # " {
    send -s "cli session auto-logout 0\r"
  }

  if { [llength $tpass] > 0 } {

    expect "(config) # " {
      send -s "\r"

    } " # " {
      send -s "conf t\r"

    }
    expect "(config) # " { send -s "tacacs key 0 $tpass\r" }
    expect "(config) # " { send -s "show tacacs\r" }
    set cpass " "
    expect -re " key: .+?\n" {
        regexp -line {key: (.+?)$} $expect_out(buffer) m cpass
    }

    return $cpass
  }
}

spawn ssh -q -o "ControlPersist no" admin@10.66.128.10
psktest ""
socket -server accept 9000
vwait event
