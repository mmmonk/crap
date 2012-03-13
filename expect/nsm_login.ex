#!/usr/bin/expect -f

# ver: 20120313
#
# ChangeLog:
# 20120313
# - added env variables NS_PRINTER_LEVEL,NSMUSER, NSMPASSWD,
# - removed the commands run automatically from history,
# - added shortcut for turning debugging without restarting,
# - option to disable encryption between the devSvr and devices,
# 20120215:
# - added all the /usr/netscreen/*/utils to the PATH,
# - added menu item to export and import the db,
# - added possible env variable NSM_LOGIN_ARCH to specify 
#   where to save the session logs,
# - various small fixes,
# 20120213:
# - added env support for easier usage of dbxml,


#### TO DO:
#
# - auto installation of NSM possible from inside this client,
# - auto log monitoring and doing an action once a pattern is found,


if {[info exists env(NSM_LOGIN_ARCH)]} {
  set logdir "$env(NSM_LOGIN_ARCH)"
} else {
  set logdir "$env(HOME)/store/work/_archives_worklogs/"
}

set send_slow {10 .01}
set timeout 90
set app nsm
set os "Linux"

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

set stime    [ timestamp -format "%Y/%m/%d %H:%M:%S"]
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
} "1-7,QR" {
  set app space
  send -s "7"
  exp_continue
} "*$ " {
  send -s "sudo su -\r"
  exp_continue
} "*# " {
  send "echo \${SHELL}\r"
}


### make sure we are running bash
expect "*#" {
  if { ! [regexp "bash" $expect_out(buffer)] } {
    send -s "bash\r"
  } else {
    send "\r"
  }
}

expect "*#" {
#  send -s "set -o vi;export HISTCONTROL=ignoredups;export PS1='\\a\[\\D{%Y-%m-%d %H:%M:%S}\]\\n\\u@\\h:\\w \\\$ ';export PROMPT_COMMAND='echo -ne \"\\a\\033_\${USER}@\${HOSTNAME%%.*}:\${PWD}\\033\\\\\"';uname\r"
  send -s "set -o vi;export HISTCONTROL=ignoredups;export PS1='\\a\[\\D{%Y-%m-%d %H:%M:%S}\]\\n\\u@\\h:\\w \\\$ ';uname\r"
}

expect "*#" {
  if { [regexp "Linux" $expect_out(buffer)] } {
    set os "Linux"
  } elseif { [regexp "SunOS" $expect_out(buffer)] } {
    set os "SunOS"
  } else {
    return
  }
  send "\r"
}

expect "*#" {
  if { $os == "Linux" } {
    if { $app == "nsm" } {
      send -s "export DB_HOME=\"/var/netscreen/GuiSvr/xdb/\";unset TMOUT;ln -sf /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime;ntpdate -u 172.30.73.133;hwclock --systohc\r"
    }
  } elseif { $os eq "SunOS" } {
    send "ntpdate -u 172.30.73.133\r"
  } else {
    send "\r"
  }
}


if { $app == "nsm" } {
  expect "*#" {
    if { $os == "Linux" } {
      send -s "ifconfig | perl -nle'/dr:(172.30.\\S+)/&&print\$1'\r"
    } elseif { $os == "SunOS" } {
      send -s "ifconfig -a | perl -nle'/net (172.30.\\S+)/&&print\$1'\r"
    }
  }

  expect "*#" {
    set ourip [regexp -inline -- {172\.30\.\d+\.\d+} $expect_out(buffer)]
    send "\r"
  }
} else {
  set ourip 127.0.0.1
  send "\r"
}

if { $app == "nsm" } {
  expect "*#" {
    send "DBXML_DIR=`ls -1 -t /usr/netscreen/GuiSvr/utils|grep dbxml| head -n 1`;\
    LD_LIBRARY_PATH=/usr/netscreen/GuiSvr/utils/\$DBXML_DIR/lib:\$LD_LIBRARY_PATH;\
    PATH=/usr/netscreen/GuiSvr/utils/\$DBXML_DIR/bin/:\$PATH:/usr/netscreen/DevSvr/utils/:/usr/netscreen/GuiSvr/utils/:/usr/netscreen/HaSvr/utils/;\
    NS_PRINTER_LEVEL=debug;\
    NSMUSER=\"global/super\";\
    NSMPASSWD=\"netscreen\";\
    export LD_LIBRARY_PATH PATH NS_PRINTER_LEVEL NSMUSER NSMPASSWD;\
    history -r ~/.bash_history\r"
  }
}

expect "*# " {
  log_file "$logdir/$host-$filetime.log"
  send_log "\n---------- log start at $stime ----------\n"

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
        } eof {
          return
        } "*# " {
          send "exit\r"
          exp_continue
        } "*$ " { 
          send "exit\r" 
          sleep 1
          return
        }
      } 
      if { $app == "space" } {
        expect timeout {
          set timeout 60
        } ",QR" {
          send "q"
          sleep 1
          return
        }
      }
    }

    \001h { 
      send_user "
--- Help ---

IP that will be used during the installation is: $ourip

Ctrl+a h - this message,
Ctrl+a c - menu choice, including removal, cleanup, db changes and corrections,  
Ctrl+a d - turning on all possible debugging while the processes are running, 
Ctrl+a i - can be entered during the nsm installation will answer all the questions (clean install Gui+Dev if installing from scratch or just refresh otherwise),
Ctrl+a x - stop/status/start/restart/version on all three services,
Ctrl+a t - prints current timestamp in the format %Y%m%d%H%M%S suitable for naming backups/copies of files,
"
      send "\r"
    }

    \001x { 
      send_user "\nType the action (stop/status/start/restart/version):"
      stty cooked echo 
      expect_user -re "(.*)\n"
      stty raw -echo
      set action $expect_out(1,string)
      send -s "/etc/init.d/guiSvr $action; /etc/init.d/devSvr $action; /etc/init.d/haSvr $action\n"
    }
   
    \001d {
      send -s "cd /usr/netscreen/GuiSvr/utils/ && ./debugConsole\n"
      
      expect "Server mgtsvr is now connected phase" { send -s "\n" }
      
      expect "relay>" { 
        send -s "mgtsvr\n" 
      } "*#" {
        send -s "\n"
      }
      
      expect "mgtsvr>" { 
        send -s "set printer levels debug\n" 
      } "No command" { 
        send -s "devsvr\n" 
      } "*#" {
        send -s "\n"
      }
      
      expect "mgtsvr>" { 
        send -s "devsvr\n"
        exp_continue
      } "devsvr>" {
        send -s "set printer levels debug\n"
      } "No command" {
        send -s "\n"
      } "*#" {
        send -s "\n"
      }

      expect "mgtsvr>" {
        send -s "local\n"
        exp_continue
      } "devsvr>" {
        send -s "local\n"
        exp_continue
      } "relay>" {
        send -s "quit really\n"
      } "*#" {
        send -s "\n"
      }

      expect "*#" { send -s "/usr/netscreen/GuiSvr/utils/guiSvrCli.sh --gdh-debug --debug\n"}
      expect "*#" { send -s "/usr/netscreen/DevSvr/utils/devSvrCli.sh --ddh-debug --debug\n"}

    }
    \001t {
      set backuptime [ timestamp -format "%Y%m%d_%H%M%S"]
      send -s "$backuptime"
    }

    \001c {
      send_user "\nType the action number:
 1 - correct /usr/netscreen/DevSvr/var/devSvr.cfg by removing unneeded white characters (make a copy) and restart DevSvr,
 2 - truncate the schema,
 3 - correct the customer db (super password, IPs),
 4 - prepare a command that will uninstall all NSM packages and remove all the NSM data from the server, the command is printed without \\r at the end,
 5 - print the command needed to export the db to xdif ($filetime),
 6 - print the command needed to import the db from xdif ($filetime),
 7 - disables encryption between devSvr and the devices,

 input: "
      stty cooked echo 
      expect_user -re "(.*)\n"
      stty raw -echo
      set action $expect_out(1,string)

      send "\r"
      
      # devsvr.cfg corrections of whitespaces
      if { $action == 1 } {
      
        set backuptime [ timestamp -format "%Y%m%d_%H%M%S"]
        send "/etc/init.d/devSvr stop; perl -pi\".$backuptime\" -e 's/  +/ /g' /usr/netscreen/DevSvr/var/devSvr.cfg && /etc/init.d/devSvr start\r" 
     
      # truncate schema
      } elseif { $action == 2 } {
        send "history -w ~/.bash_history\r"
        expect "*# " { send "/etc/init.d/haSvr stop\r"}
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
        expect "*# " { send "/etc/init.d/devSvr start;history -r ~/.bash_history\r"}

      # correct the customer db (super password, IPs)
      } elseif { $action == 3 } {
        send "history -w ~/.bash_history\r"
        expect "*# " { send "/etc/init.d/haSvr stop\r"}
        expect "*# " { send "/etc/init.d/devSvr stop\r"}
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
        expect "*# " { send "perl -npi\".old_$backuptime\" -e 's/ +/ /g;\
        s/(clientOneTimePassword\\s+)\\S*/\$1 dk2003ns/i;\
        s/(default.printLevel\\s+)\\S*/\$1 debug/i;\
        s/(ourRsaPrivateKey|theirRsaPublicKey)/#\$1/i;\
        s/(guiSvrDirectiveHandler.max.heap|devSvrDirectiveHandler.max.heap\\s*) \\d+/\$1 1536000000/i' /var/netscreen/*Svr/*Svr.cfg > /dev/null\r"}
        expect "*# " { send "/etc/init.d/haSvr restart\r"}
        expect "*# " { send "/etc/init.d/devSvr restart\r"}
        expect "*# " { send "/etc/init.d/guiSvr restart;history -r ~/.bash_history\r"}

      # NSM removal
      } elseif { $action == 4 } {
        if { $os == "Linux" } {
          send -s "rpm -qa | grep netscreen | xargs -r rpm -e ; rm -rf /var/netscreen/*/* /usr/netscreen/*" 
        } elseif { $os == "SunOS" } {
          send -s "pkgrm -n `pkginfo -c application | grep -i netscreen | grep -v NSCNpostgres | awk '{print \$2}' | xargs` &&  rm -rf /var/netscreen/ /usr/netscreen/"
        } 
      } elseif { $action == 5 } {
        send -s "/usr/netscreen/GuiSvr/utils/xdbExporter.sh /var/netscreen/GuiSvr/xdb/ /var/tmp/xdif_$filetime.txt "

      } elseif { $action == 6 } {  
        send -s "/usr/netscreen/GuiSvr/utils/xdifImporter.sh /var/tmp/xdif_$backuptime.txt /var/netscreen/GuiSvr/xdb/init/ "

      } elseif { $action == 7 } {
        set backuptime [ timestamp -format "%Y%m%d_%H%M%S"]
        send -s "/etc/init.d/devSvr stop; perl -pi\".$backuptime\" -e 's/(devSvrManager.cryptoKeyLength\\s*) \\d+/\$1 0/' /usr/netscreen/DevSvr/var/devSvr.cfg && /etc/init.d/devSvr start\r"

      # default - unknown choice
      } else {
        send_user "\nUnknown choice\n"
      }
    }

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
      } "Enter the https port for web server *>" {
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
      } "Specify location of PostgreSQL * bin *> " {
        send "\r"
        exp_continue
      }
    }
  }
}

set time     [ timestamp -format "%Y/%m/%d %H:%M:%S"]
send_log "\n---------- log close at $time ----------\n"
log_file
exec /bin/bzip2 $logdir/$host-$filetime.log
send_user "\n\[+\] session lasted from $stime to $time\n\[+\] logfile: $logdir/$host-$filetime.log.bz2\n" 
exit

