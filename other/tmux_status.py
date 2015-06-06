#!/usr/bin/env python

# $Id: 20130606$
# $Date: 2013-06-06 21:37:01$
# $Author: Marek Lukaszuk$

#from time import strftime,tzset
from os import environ, statvfs
from os.path import exists as fs_exists, ismount
import time

#tzlist = ["America/Los_Angeles","America/New_York","GMT","Asia/Kolkata","Asia/Tokyo","Pacific/Auckland"]
mntlist = ["/","/home"]

txt = ""

## timezone information
#for tz in tzlist:
#  environ['TZ'] = tz
#  txt+=strftime("%H%M")+strftime("%Z")[0]+" "

## disk usage
for path in mntlist:
  if ismount(path):
    st = statvfs(path)
    #free = (st.f_bavail * st.f_frsize)
    total = (st.f_blocks * st.f_frsize)
    used = (st.f_blocks - st.f_bfree) * st.f_frsize
    try:
      percent = int((float(used) / total) * 100)
    except ZeroDivisionError:
      percent = 0
    txt+=str(path)+":"+str(percent)+"% "

## thermal information
## laptop
try:
  txt += str(int(open("/sys/devices/virtual/thermal/thermal_zone0/temp").readline())/1000)+"C "
except:
  pass

## thermal work
##
try:
  t1 = int(open("/sys/devices/platform/coretemp.0/temp2_input").readline())/1000
  t2 = int(open("/sys/devices/platform/coretemp.0/temp3_input").readline())/1000
  t3 = int(open("/sys/devices/platform/coretemp.3/temp2_input").readline())/1000
  t4 = int(open("/sys/devices/platform/coretemp.3/temp3_input").readline())/1000
  txt += str((t1+t2+t3+t4)/4)+"C "
except:
  pass

## battery information
## TODO: maybe use the /sys/ filesystem to dig out this information?
if fs_exists("/sys/devices/LNXSYSTM:00/LNXSYBUS:00/PNP0C0A:00/power_supply/BAT0"):

  try:
    dmax = float(open("/sys/devices/LNXSYSTM:00/LNXSYBUS:00/PNP0C0A:00/power_supply/BAT0/charge_full_design").read().strip())
    cmax = float(open("/sys/devices/LNXSYSTM:00/LNXSYBUS:00/PNP0C0A:00/power_supply/BAT0/charge_full").read().strip())
    cur = float(open("/sys/devices/LNXSYSTM:00/LNXSYBUS:00/PNP0C0A:00/power_supply/BAT0/charge_now").read().strip())
    bstat = open("/sys/devices/LNXSYSTM:00/LNXSYBUS:00/PNP0C0A:00/power_supply/BAT0/status").read().strip()
  except:
    dmax = 1.0
    cmax = 1.0
    cur = 1.0
    bstat = "-"

  if bstat == "Discharging":
    #h = cur/rate
    txt+="-"+str(round((cur/cmax)*100,2))+"%"
  elif bstat == "Charging":
    #h = (cmax-cur)/rate
    txt+="+"+str(round((cur/cmax)*100,2))+"%"   #str(int(h))+"."+str(int(60*(h-int(h))))
  elif bstat == "Full":
    txt+="="+str(round((cur/dmax)*100,2))+"%"

## data usage
if fs_exists("/var/local/datausage.dat"):
  try:
    txt += str(int(float(open("/var/local/datausage.dat","r").readline().split()[7])/1024/500*100))+"%"
  except:
    txt += "?%"

  ts = time.localtime()
  txt += "/%s%%" % (int((ts.tm_mday/31.0)*100))
print txt
