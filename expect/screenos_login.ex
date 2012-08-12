#!/usr/bin/expect --

# $Id: 20120812$
# $Date: 2012-08-12 08:02:52$
# $Author: Marek Lukaszuk$

proc help { } {
  global ip
  global name

  send_user "\033\[1;31m
----- Help -----
Connected to: $name
Current Mgt IP is: $ip

Ctrl+a h - this help,
Ctrl+a ? - also this help,

Ctrl+a c - basic config,
Ctrl+a l - auto login,
Ctrl+a i - change the IP address,
Ctrl+a d - quit,\033\[m

"
}

proc curtime { } {
  return [ timestamp -format "%Y/%m/%d %H:%M:%S"]
}

proc backuptimeproc { } {
  return [ timestamp -format "%Y%m%d_%H%M%S"]
}

# set send_slow  {2  .001}
set send_slow {10 .01}
set timeout 60

if { $argc == 0 } {
  exit
} else {
  set host [lindex $argv 0]
  set port "23"
  set name [lindex $argv 0]
  if { $argc > 1 } {
    set port [lindex $argv 1]
  }
  if { $argc > 2 } {
    set name [lindex $argv 2]
  }
}

set pass "netscreen"
set enab "netscreen"
set user "netscreen"

set prompt "*-> "

# we are connecting to the remote host
spawn telnet $host $port
send -s "\r"

expect timeout {
	send_user "failed to connect - timeout\n"
	exit
} eof {
	send_user "failed to connect\n"
	exit
} "login*" {
	send -s "$user\r"
  exp_continue
} "assword:*" {
	send -s "$pass\r"
  exp_continue
} "*-> " {
	send -s "\r"

}

set time     [ curtime ]
set filetime [ backuptimeproc ]

# xterm title change
send_user "\033]2;$name $filetime\007"

set fp [open "/etc/hosts" r]
while { [gets $fp line] >=0 } {
	if {[regexp $name $line]} {
		set line [split $line " "]
		set ip [lindex $line 0]
	}
}
close $fp
send_user "\n\033\[1;33m$name IP is $ip\nCtrl+a h - for help\033\[m\n"

log_file "/home/case/store/work/_archives_worklogs/$name-$filetime.log"

send_log "\n---------- log start at $time ----------\n"

interact {
	# so that we don't get logout when idle
	# timeout 180 { send " \b"}
	\004 {
		send_user "\nbye, bye\n"
		set pid [exp_pid]
		system "kill $pid"
	}

	\001l {
		send -s "\r"
		expect  "login*" {
			send -s "$user\r"
		  exp_continue
    } "assword:*" {
			send -s "$pass\r"
      exp_continue
		} "*-> " {
			send -s "\r"
		}

	}
  \001h {
    help
  }
  \001? {
    help
  }
	\001i {
    send_user "\nThe new mgt IP: "

    stty cooked echo
    expect_user -re "(.*)\n"
    stty raw -echo
    global ip
    set ip $expect_out(1,string)
    send "\r"
  }
	\001c {
		send -s "set clock [curtime]\r"
		expect "$prompt"
		send -s "set hostname lab-$name\r"
		expect "$prompt"
		send -s "set interface mgt ip $ip/23\r"
		expect "$prompt"
		send -s "set interface eth0 ip $ip/23\r"
		expect "$prompt"
		send -s "set interface eth0/0 ip $ip/23\r"
		expect "$prompt"
		send -s "set interface eth0 manage\r"
		expect "$prompt"
		send -s "set interface eth0/0 manage\r"
		expect "$prompt"
		foreach cmd {	"set console page 0"
				"set console timeout 0"
				"set dbuf size 4096"
				"set admin name netscreen"
				"set admin password netscreen"
				"set admin auth server \"Local\""} {
			send -s "$cmd\r"
			expect "$prompt"
		}
		foreach alias {	"ss \"save software from tftp 172.30.73.133\""
				"sc \"save config from tftp 172.30.73.133\""
        "sh \"get\""
				"wr \"save\""
				"reload \"reset no-prompt\""
        "q \"exit\""} {
			send -s "set alias $alias\r"
			expect "$prompt"
		}
	}
# 	\0010 {
# 		set timeout 3600
# 		match_max 10240000
# 		send -s "get tech-support\r"
# 		expect "$prompt"
# 		send -s "get event\r"
# 		expect "$prompt"
# 		send -s "get log sys\r"
# 		expect "$prompt"
# 		send -s "get nsrp\r"
# 		expect "$prompt"
# 		send -s "get nsrp monitor\r"
# 		expect "$prompt"
# 		send -s "get interface\r"
#
# 		for { set x 1 } { $x<=4 } { incr x } {
#
# 			expect "$prompt"
# 			send -s "get nsrp\r"
# 			expect "$prompt"
# 			send -s "get nsrp counter\r"
# 			expect "$prompt"
# 			send -s "get nsrp coun packet\r"
# 			expect "$prompt"
# 			send -s "get interface\r"
# 		}
#
#
# 		expect "$prompt"
# 		send -s "get db stream\r"
# 		expect "$prompt"
# 		sleep 5
# 		match_max -d
# 		set timeout 30
# 	}
	\001t {
		set timeout 3600
		set prompt "*-> "
		for { set x 1 } { $x<=130 } { incr x } {
			send -s "set route 10.0.$x.0/24 interface eth0/0 gateway 172.30.72.1\r"
			expect "$prompt"
			sleep 1
		}
		send_user "\ndone\n"
		send -s "\r"
		set timeout 30
	}


	\001g {
		set timeout 3600
		set prompt "*-> "
		for { set x 1 } { $x<=2 } { incr x } {
			send -s "get clock\r"
			expect "$prompt"
			sleep 10
		}
		send_user "\ndone\n"
		send -s "\r"
		set timeout 30
	}


	\177 {
		send "\010"
	}
	"\033\[3~" {
		send "\177"
	}
}

set time [ curtime ]
send_log "\n---------- log close at $time ----------\n"
log_file
exec /bin/bzip2 /home/case/store/work/_archives_worklogs/$name-$filetime.log
exit
