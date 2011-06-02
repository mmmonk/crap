#!/usr/bin/expect -f

# $Id$

set send_slow {10 .01}
set timeout 60
set app nsm

if { $argc == 0 } {
  puts "
Usage: $argv0 <username@>host <password>

If not specified username defaults to \"root\" and password to \"netscreen\".

The connection to target host is done with normal ssh command without any arguments. 
My suggestion is to use ~/.ssh/config for any non standard options.
" 
  exit
} else {
  set host [lindex $argv 0]
  set user "root"
  set pass "netscreen"
  if { [regexp @ $host] } {
    regexp {(\S+?)@} $host match user
    regexp {@(\S+)} $host match host
  }
  if { $argc > 1 } {
    set pass [lindex $argv 1]
  }
}

spawn ssh $user@$host

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
set filetime [ timestamp -format "%Y%m%d_%H%M%S"]

puts "\033]0;$host $filetime\007"

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
  set app nsm 
  send -s "n"
  exp_continue
} "1-6,QR" {
  set app space
  send -s "6"
  exp_continue
} "*$ " {
  send -s "sudo su -\r"
  exp_continue
} "*# " {
  if { $app == "nsm" } {
    send -s "unset TMOUT;ln -sf /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime;ntpdate -u 172.30.73.133;hwclock --systohc\r"
  } else {
    send "\r"
  }
}

if { $app == "nsm" } {
  expect "*#" {
    send "ifconfig | perl -nle'/dr:(172.30.\\S+)/&&print\$1'\r"
  }

  expect "*#" {
    set ourip [regexp -inline -- {172\.30\.\d+\.\d+} $expect_out(buffer)]
    send "\r"
  }
} else {
  set ourip 127.0.0.1
}

expect "*# " {
  log_file "/home/case/store/work/_archives_worklogs/$host-$filetime.log"
  send_log "\n---------- log start at $time ----------\n"
  send_user "\n---------- session start at $time ----------\n"

  send_user "
--- Help key ---
Ctrl+a h - all shortcuts\n"

  send "\r"


  interact {

    \003  { send "\003" }
    \004  { send "exit\r" 
      set timeout 10
      if { $app == "nsm" } { 
        expect timeout {
          set timeout 60
        } "*$ " { 
          send "exit\r" 
          sleep 1
          return
        }
      } 
      if { $app == "space" } {
        expect timeout {
          set timeout 60
        } "1-6,QR" {
          send "q"
          sleep 1
          return
        }
      }
    }

    \001h { send_user "
--- Help ---

IP that will be used during the installation is: $ourip

Ctrl+a h - this message
Ctrl+a i - can be entered during the nsm installation will answer all the questions (clean install Gui+Dev if installing from scratch or just refresh otherwise)
Ctrl+a l - types \"netscreen\\r\"
Ctrl+a p - types \"rpm -qa | grep netscreen | xargs -r rpm -e ; rm -rf /var/netscreen/*/* /usr/netscreen/*\" <- notice no \\r
Ctrl+a t - truncate the schema
Ctrl+a u - correct the customer db (super password, IPs)

" 
    send "\r"
    }

    \001l { send "$pass\r" }

    \001p { send "rpm -qa | grep netscreen | xargs -r rpm -e ; rm -rf /var/netscreen/*/* /usr/netscreen/*" }

    \001i { 
        send  "\r"
        expect timeout {
          send_user " "
        } "Do you want to do NSM installation with base license? (y/n) *>" {
          send "y\r" 
          exp_continue
        } "Enter selection (1-2)*>" {
          send "2\r"
          exp_continue
        } "Will server(s) need to be reconfigured during the refresh? (y/n) *>" {
          send "n\r"
          exp_continue 
        } "Enter selection (1-3)*>" {
          send "3\r" 
          exp_continue
        } "Enter base directory location for management servers " {
          send "\r"
          exp_continue 
        } "Enable FIPS Support? (y/n)*>" {
          send "n\r"
          exp_continue
        } "Will this machine participate in an HA cluster? (y/n) *>" {
          send "n\r"
          exp_continue 
        } "Enter database log directory location *>" {
          send "\r"
          exp_continue
        } "Enter the management IP address of this server *>" {
          send "$ourip\r"
          exp_continue
        } "Enter the https port for NBI service *>" {
          send "\r"
          exp_continue
        } "Enter password (password will not display as you type)>" {
          send "$pass\r"
          exp_continue
        } "Will a Statistical Report Server be used with this GUI Server? (y/n) *>" {
          send "n\r"
          exp_continue
        } "UNIX password: " {
          send "$pass\r"
          exp_continue
        } "Will server processes need to be restarted automatically in case of a failure? (y/n) *>" {
          send "n\r"
          exp_continue
        } "Will this machine require local database backups? (y/n) *>" {
          send "n\r"
          exp_continue
        } "Enter Postgres DevSvr Db port *> " {
          send "\r"
          exp_continue
        } "Enter Postgres DevSvr Db super user *> " {
          send "\r"
          exp_continue
        } "Start server(s) when finished? (y/n) *> " {
          send "y\r"
          exp_continue
        } "Are the above actions correct? (y/n)> " {
          send "y\r"
          exp_continue
        }
    }

    \001t {
      send "/etc/init.d/haSvr stop\r"
      expect "*# " { send "/etc/init.d/guiSvr stop\r"}
      expect "*# " { send "/etc/init.d/devSvr stop\r"}
      #expect "*# " { send "mv -f /usr/netscreen/GuiSvr/var/dmi-schema-stage /usr/netscreen/GuiSvr/var/dmi-schema-stage.old\r"}
      expect "*# " { send "rm -rf /usr/netscreen/GuiSvr/var/dmi-schema-stage\r"}
      expect "*# " { send "cp --reply=yes -fpr /usr/netscreen/GuiSvr/lib/initVar/dmi-schema-stage /usr/netscreen/GuiSvr/var/dmi-schema-stage\r"}
      expect "*# " { send "rm -f /usr/netscreen/GuiSvr/var/xdb/init/*\r"}
      expect "*# " { send "rm -rf /tmp/Schemas*\r"}
      expect "*# " { send "rm -rf /usr/netscreen/GuiSvr/var/Schemas-GDH/*\r"}
      expect "*# " { send "sh /usr/netscreen/GuiSvr/utils/.truncateSchemaTables.sh /usr/netscreen/GuiSvr/var/xdb\r"}
      expect "*# " { send "cp --reply=yes -fpr /usr/netscreen/GuiSvr/lib/initVar/xdb/init/* /usr/netscreen/GuiSvr/var/xdb/init/\r"}
      expect "*# " { send "/etc/init.d/haSvr start\r"}
      expect "*# " { send "/etc/init.d/guiSvr start\r"}
      expect "*# " { send "/etc/init.d/devSvr start\r"}
    }

    \001u { 
      send "/etc/init.d/haSvr stop\r"
      expect "*# " { send "/etc/init.d/guiSvr stop\r"}
      expect "*# " { send "/usr/netscreen/GuiSvr/utils/setperms.sh GuiSvr > /dev/null\r"}
      expect "*# " { send "/bin/chmod +s /usr/netscreen/GuiSvr/utils/.installIdTool\r"}
      expect "*# " { send "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb admin 1 0 /__/password \"glee/aW9bOYEewkD/6Ri8sHh2mU=\" > /dev/null\r"}
      sleep 1
      expect "*# " { send "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb server 0 0 /__/ip \"$ourip\" > /dev/null\r"}
      sleep 1
      expect "*# " { send "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb server 0 1 /__/ip \"$ourip\" > /dev/null\r"}
      sleep 1
      expect "*# " { send "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb shadow_server 0 1 /__/clientOneTimePassword \"dk2003ns\" > /dev/null\r"} 
      sleep 1
      set backuptime [ timestamp -format "%Y%m%d_%H%M%S"]
      expect "*# " { send "perl -npi\".old_$backuptime\" -e 's/ +/ /g;s/(clientOneTimePassword\\s+)\\S*/\$1 dk2003ns/i;s/(default.printLevel\\s+)\\S*/\$1 debug/i;s/(ourRsaPrivateKey|theirRsaPublicKey)/#\$1/i;s/(guiSvrDirectiveHandler.max.heap|devSvrDirectiveHandler.max.heap\\s+)\\d+/\$1 1536000000/i' /var/netscreen/*Svr/*Svr.cfg > /dev/null\r"}
      expect "*# " { send "/etc/init.d/haSvr restart\r"}
      expect "*# " { send "/etc/init.d/guiSvr restart\r"}
      expect "*# " { send "/etc/init.d/devSvr restart\r"}
    }
  }
}

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
send_log "\n---------- log close at $time ----------\n"
log_file
exec /bin/bzip2 /home/case/store/work/_archives_worklogs/$host-$filetime.log
send_user "\n---------- session closed at $time ----------\n"
exit

