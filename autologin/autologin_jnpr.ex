#!/usr/bin/expect --

;# Author: Marek Lukaszuk <m.lukaszuk<at>gmail.com>
;# Copyright (c) 2007, Marek £ukaszuk 
;# BSD License at http://monkey.geeks.pl/bsd/

;# package require base64

;# set send_slow  {2  .001}
set send_slow {10 .01}
set timeout 60

if { $argc == 3 } {
	set host [lindex $argv 0]
	set port [lindex $argv 1]
	set name [lindex $argv 2]
} else {
	if { $argc == 2 } {
		set host [lindex $argv 0]
		set port [lindex $argv 1]
		set name [lindex $argv 0]
	} else {
		if { $argc == 1} {
			set host [lindex $argv 0]
			set port "23"
			set name [lindex $argv 0]
		} else {
			exit;
		}
	}
}

set pass "netscreen"
set enab "netscreen"
set user "netscreen"

set prompt "*-> "

send_user "CTRL+a
c - basic config
i - show ip address
l - auto login
q - quit
"

;# we are connecting to the remote host
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
	expect "assword:*" { 
		send -s "$pass\n"
	} 
} "assword:*" { 
	send -s "$pass\r" 

} "*-> " { 
	send -s "\r" 

}

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
set filetime [ timestamp -format "%Y%m%d_%H%M%S"]

;#send_user "\nLogin time is $time\n"

;# xterm title change
send_user "\033]2;$name $filetime\007"

set fp [open "/etc/hosts" r]
while { [gets $fp line] >=0 } {
	if {[regexp $name $line]} {
		set line [split $line "\t"]
		set ip [lindex $line 0]
	}
}
close $fp
send_user "\n$name IP is $ip\n"


log_file "/home/case/store/work/_archives_worklogs/$name-$filetime.log"

send_log "\n---------- log start at $time ----------\n"

interact {
	\001q {
		send_user "\nbye, bye\n"
		set pid [exp_pid]
		system "kill $pid"
	}

	\001l {
		send -s "\r"		
		expect  "login*" {
			send -s "$user\r"
			expect "assword:*" {
				send -s "$pass\n"
			}
		} "assword:*" {
			send -s "$pass\r"
		} "*-> " {
			send -s "\r"
		}

	}
	\001i {
		send_user "\n$name IP is $ip\n"
	}
	\001c {
		set curtime [ timestamp -format "%m/%d/%Y %H:%M:%S"]
		send -s "set clock $curtime\r"
		expect "$prompt"
		send -s "set hostname $name\r"
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
		foreach alias {	"sg \"save config to last-known-good\""
				"ss \"save software from tftp 172.30.73.133\""
				"sc \"save config from tftp 172.30.73.133\""
				"cl \"clear db\""
				"gd \"get db stream\""
				"gs \"get sys\""} {
			send -s "set alias $alias\r"
			expect "$prompt"
		}
	}
	\177 {
		send "\010"
	}
	"\033\[3~" {
		send "\177"
	}
}

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
send_log "\n---------- log close at $time ----------\n"
log_file
exec /bin/bzip2 /home/case/store/work/_archives_worklogs/$name-$filetime.log
exit
