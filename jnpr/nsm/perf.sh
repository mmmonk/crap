#!/bin/sh

# $Id$

IFS=""

CURDATE=`date +%Y%m%d_%H%M%S`
LOGFILE="/tmp/nsm-tech-support-${CURDATE}.txt.gz"

cmdrun()
{
  echo "-=-=-=-=-=-=-=-=- $1 -=-=-=-=-=-=-=-=-"
  eval $1
}

(
for cmd in "mount" "df -h" "free" "uptime" "uname -a" "sysctl -a" "ifconfig" "dmesg" "netstat -nlp" "iptables -nvL"
do
  cmdrun $cmd
done

echo "-=-=-=-=-=-=-=-=- xdb size -=-=-=-=-=-=-=-=-"
if [ "${NSROOT}x" != "x" ]; then
  du -sh ${NSROOT}/GuiSvr/xdb/data
  ls -l ${NSROOT}/GuiSvr/xdb/data | sort -rnk5 
else
  du -sh /var/netscreen/GuiSvr/xdb/data
  ls -l /var/netscreen/GuiSvr/xdb/data | sort -rnk5
fi 

for (( i = 1; i <= 10; i++ ))
do
  cmdrun date
  cmdrun "top -b -H -n 1"
  cmdrun "ps auxm"
  cmdrun "vmstat 1 10"
  cmdrun "netstat -ni"

  sleep 10
done

cmdrun "/etc/init.d/guiSvr version || /etc/init.d/devSvr version" 
) | gzip -c > $LOGFILE


echo "The output is saved in $LOGFILE, please attach it to your case."
