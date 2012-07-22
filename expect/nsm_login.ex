#!/usr/bin/expect -f

# $Id: 20120722$
# $Date: 2012-07-22 08:46:56$
#
# ChangeLog:
# 20120719
# - default user changed to "admin",
# - added menu to change the default IP address picked by the script,
# - more aliases,
# 20120403
# - added some aliases for often used commands (jtac_),
# - backup is automatically disabled in xdifImporter.sh,
# - less garbage on the screen while login in,
# - reads the /home/admin/.info file used in EMEA,
# - removal of the "safe" aliases for rm, mv and cp,
# - some small code improvements,
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

proc curtime { } {
  return [ timestamp -format "%Y/%m/%d %H:%M:%S"]
}

proc backuptimeproc { } {
  return [ timestamp -format "%Y%m%d_%H%M%S"]
}

proc online_help {ourip} {
      send_user "
--- Help ---

IP that will be used during the installation is: $ourip

Ctrl+a h - this message,
Ctrl+a ? - also this message ;),
Ctrl+a c - menu choice, including removal, cleanup, db changes and corrections,
Ctrl+a d - turning on all possible debugging while the processes are running,
Ctrl+a i - can be entered during the nsm installation will answer all the questions (clean install Gui+Dev if installing from scratch or just refresh otherwise),
Ctrl+a x - stop/status/start/restart/version on all three services,
Ctrl+a t - prints current timestamp in the format %Y%m%d%H%M%S suitable for naming backups/copies of files,

and check also jtac_ cli commands

"
      send "\r"
}


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
  set user "admin"
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

#puts "\033]0;$host $filetime\007"

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

log_user 0

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
      # export DB_HOME=\"/var/netscreen/GuiSvr/xdb/\" # <- this causes issues during install
      send -s "unset TMOUT;ln -sf /usr/share/zoneinfo/Europe/Amsterdam /etc/localtime;date -s \"[curtime]\";hwclock --systohc\r"
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
    perl -i -pe 's/(^gzip|^tar)/#\$1/' /usr/netscreen/GuiSvr/utils/xdifImporter.sh;\
    alias jtac_export_import_xdb='/usr/netscreen/GuiSvr/utils/xdbExporter.sh /var/netscreen/GuiSvr/xdb/ /var/tmp/xdif_$filetime.txt && /usr/netscreen/GuiSvr/utils/xdifImporter.sh /var/tmp/xdif_$filetime.txt /var/netscreen/GuiSvr/xdb/init/';\
    function jtac_all_proc() { /etc/init.d/guiSvr \$1; /etc/init.d/devSvr \$1; /etc/init.d/haSvr \$1; };\
    alias jtac_debug_env='export NS_PRINTER_LEVEL=debug';\
    alias jtac_undebug_env='unset NS_PRINTER_LEVEL';\
    alias jtac_nsm_ps='ps -U nsm -u nsm u';\
    alias xdbViewEdit=/usr/netscreen/GuiSvr/utils/.xdbViewEdit.sh;\
    alias jtac_db_size='ls -lrhS /var/netscreen/GuiSvr/xdb/data/';\
    function jtac_import() { /usr/netscreen/GuiSvr/utils/xdifImporter.sh \$1 /var/netscreen/GuiSvr/xdb/init/; };\
    alias jtac_export=/usr/netscreen/GuiSvr/utils/xdbExporter.sh /var/netscreen/GuiSvr/xdb/ ;\
    alias jtac_edit=/usr/netscreen/GuiSvr/utils/.xdbViewEdit.sh;\
    function jtac_extract_contariner_from_xdif() { perl -e '\$a=0;\$b=shift;while(<>){\$a=0 if (/^END/); \$a=1 if (/^\$b/);print if (\$a==1);}' \$1 \$2; };\
    function jtac_container_xdif_to_init() { perl -ne 'if (/^\\)/){ print \"#####TUPLE_DATA_END#####\\n\"; next; } if (/^\\((.{8})(.{4})(.{4})\\s*/){ print \"#####TUPLE_DATA_BEGIN#####\\n\"; print hex(\$1),\"\\n\",hex(\$3),\"\\n\"; next; } next if (/^\\S+/); s/^\\t//; s/^: \\d+\\s+//; print;' \$1; };\
    unalias rm;unalias mv;unalias cp;\r"
  }
  expect "*#" {
    send "alias ls='ls -A --time-style=long-iso --color=auto -F';\
    alias i='egrep -I -i --color=auto';\
    alias e='i -v';\
    alias findf='find . -type f -iname';\
    alias less='less -sWr';\
    alias pstree='ps axjf';\
    alias difft='diff --strip-trailing-cr -ibBw';\
    function ttail() { tail -f \$* | while read; do echo \"\$(date +%T) \$REPLY\"; done; };\r"
  }
  sleep 0.5;
  expect "*#" {
    send "if \[ -f /home/admin/.info \]; then\
    echo;echo \"+++++++++++++++++++++++++++++++++++++++++++++++++++\";\
    cat /home/admin/.info;\
    echo \"+++++++++++++++++++++++++++++++++++++++++++++++++++\";echo;fi;\
    history -r ~/.bash_history\r"
  }
}

set send_slow {5 .01}
log_user 1

expect "*# " {
  log_file "$logdir/$host-$filetime.log"
  send_log "\n---------- log start at $stime ----------\n"

  send_user "
--- Help key ---
Ctrl+a h - all shortcuts
and remember the jtac_ commands\n"

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
      online_help $ourip
    }
    \001? {
      online_help $ourip
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
      send -s [backuptimeproc]
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
 8 - set the IP used by this server, if not autodetected,

 input: "
      stty cooked echo
      expect_user -re "(.*)\n"
      stty raw -echo
      set action $expect_out(1,string)

      send "\r"

      # devsvr.cfg corrections of whitespaces
      if { $action == 1 } {
        send "/etc/init.d/devSvr stop; perl -pi\".[backuptimeproc]\" -e 's/  +/ /g' /usr/netscreen/DevSvr/var/devSvr.cfg && /etc/init.d/devSvr start\r"

      # truncate schema
      } elseif { $action == 2 } {
        send -s "history -w ~/.bash_history\r"
        expect "*# " { send -s "/etc/init.d/haSvr stop\r"}
        expect "*# " { send -s "/etc/init.d/guiSvr stop\r"}
        expect "*# " { send -s "/etc/init.d/devSvr stop\r"}
        #expect "*# " { send -s "mv -f /usr/netscreen/GuiSvr/var/dmi-schema-stage /usr/netscreen/GuiSvr/var/dmi-schema-stage.old\r"}
        expect "*# " { send -s "rm -rf /usr/netscreen/GuiSvr/var/dmi-schema-stage\r"}
        expect "*# " { send -s "cp --reply=yes -fpr /usr/netscreen/GuiSvr/lib/initVar/dmi-schema-stage /usr/netscreen/GuiSvr/var/dmi-schema-stage\r"}
        expect "*# " { send -s "rm -f /usr/netscreen/GuiSvr/var/xdb/init/*\r"}
        expect "*# " { send -s "rm -rf /tmp/Schemas*\r"}
        expect "*# " { send -s "rm -rf /usr/netscreen/GuiSvr/var/Schemas-GDH/*\r"}
        expect "*# " { send -s "sh /usr/netscreen/GuiSvr/utils/.truncateSchemaTables.sh /usr/netscreen/GuiSvr/var/xdb\r"}
        expect "*# " { send -s "cp --reply=yes -fpr /usr/netscreen/GuiSvr/lib/initVar/xdb/init/* /usr/netscreen/GuiSvr/var/xdb/init/\r"}
        expect "*# " { send -s "history -r ~/.bash_history\r"}

      # correct the customer db (super password, IPs)
      } elseif { $action == 3 } {
        send -s "history -w ~/.bash_history\r"
        expect "*# " { send -s "/etc/init.d/haSvr stop\r"}
        expect "*# " { send -s "/etc/init.d/devSvr stop\r"}
        expect "*# " { send -s "/etc/init.d/guiSvr stop\r"}
        expect "*# " { send -s "/usr/netscreen/GuiSvr/utils/setperms.sh GuiSvr > /dev/null\r"}
        expect "*# " { send -s "/bin/chmod +s /usr/netscreen/GuiSvr/utils/.installIdTool\r"}
        expect "*# " { send -s "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb admin 1 0 /__/password \"glee/aW9bOYEewkD/6Ri8sHh2mU=\" > /dev/null\r"}
        sleep 1
        expect "*# " { send -s "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb server 0 0 /__/ip \"$ourip\" > /dev/null\r"}
        sleep 1
        expect "*# " { send -s "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb server 0 1 /__/ip \"$ourip\" > /dev/null\r"}
        sleep 1
        expect "*# " { send -s "/usr/netscreen/GuiSvr/utils/.xdbUpdate.sh /usr/netscreen/GuiSvr/var/xdb shadow_server 0 1 /__/clientOneTimePassword \"dk2003ns\" > /dev/null\r"}
        sleep 1
        expect "*# " { send -s "perl -npi\".old_[backuptimeproc]\" -e 's/ +/ /g;\
        s/(clientOneTimePassword\\s+)\\S*/\$1 dk2003ns/i;\
        s/(default.printLevel\\s+)\\S*/\$1 debug/i;\
        s/(ourRsaPrivateKey|theirRsaPublicKey)/#\$1/i;\
        s/(guiSvrDirectiveHandler.max.heap|devSvrDirectiveHandler.max.heap\\s*) \\d+/\$1 1536000000/i' /var/netscreen/*Svr/*Svr.cfg > /dev/null;\
        perl -i -pe 's/(^gzip|^tar)/#\$1/' /usr/netscreen/GuiSvr/utils/xdifImporter.sh;\
        history -r ~/.bash_history\r"}

      # NSM removal
      } elseif { $action == 4 } {
        if { $os == "Linux" } {
          send -s "rpm -qa | grep netscreen | xargs -r rpm -e ; rm -rf /var/netscreen/*/* /usr/netscreen/*"
        } elseif { $os == "SunOS" } {
          send -s "pkgrm -n `pkginfo -c application | grep -i netscreen | grep -v NSCNpostgres | awk '{print \$2}' | xargs` &&  rm -rf /var/netscreen/ /usr/netscreen/"
        }
      } elseif { $action == 5 } {
        send -s "unset NS_PRINTER_LEVEL;/usr/netscreen/GuiSvr/utils/xdbExporter.sh /var/netscreen/GuiSvr/xdb/ /var/tmp/xdif_$filetime.txt; export NS_PRINTER_LEVEL=debug"

      } elseif { $action == 6 } {
        send -s "/usr/netscreen/GuiSvr/utils/xdifImporter.sh /var/tmp/xdif_$filetime.txt /var/netscreen/GuiSvr/xdb/init/ "

      } elseif { $action == 7 } {
        send -s "/etc/init.d/devSvr stop; perl -pi\".[backuptimeproc]\" -e 's/(devSvrManager.cryptoKeyLength\\s*) \\d+/\$1 0/' /usr/netscreen/DevSvr/var/devSvr.cfg && /etc/init.d/devSvr start\r"

      } elseif { $action == 8 } {
        send_user "\nThe IP of this server is: "

        stty cooked echo
        expect_user -re "(.*)\n"
        stty raw -echo
        global ourip
        set ourip $expect_out(1,string)
        send "\r"

      # default - unknown choice
      } else {
        send_user "\nUnknown choice\n"
      }
    }

    \001i {
      send "\r"
      expect timeout {
        send_user " "
      } "Do you want to do NSM installation with base license? (y/n) *>" {
        send "y\r"
        exp_continue
      } "Enter selection (1-2)*>" {
        send "2\r"
        exp_continue
      } "Hit Ctrl-C to abort upgrade or ENTER to continue" {
        send "\r"
      } "Hit Ctrl-C to abort installation or ENTER to continue" {
        send "\r"
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
        send -s "$ourip\r"
        exp_continue
      } "Enter the https port for NBI service *>" {
        send "\r"
        exp_continue
      } "Enter the https port for web server *>" {
        send "\r"
        exp_continue
      } "Enter password (password will not display as you type)>" {
        send -s "$pass\r"
        exp_continue
      } "Will a Statistical Report Server be used with this GUI Server? (y/n) *>" {
        send "n\r"
        exp_continue
      } "UNIX password: " {
        send -s "$pass\r"
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
      } "Start server(s) when finished? (y/n)*" {
        send "n\r"
        exp_continue
      } "Are the above actions correct? (y/n)" {
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

