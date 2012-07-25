#!/usr/bin/env python 

# $Id: 20120725$
# $Date: 2012-07-25 21:06:39$
# $Author: Marek Lukaszuk$

from time import strftime,tzset
from os import environ, statvfs
from os.path import exists as fs_exists, ismount

tzlist = ["America/Los_Angeles","America/New_York","GMT","Asia/Kolkata","Asia/Tokyo","Pacific/Auckland"]
mntlist = ["/","/home"]

txt = ""

## timezone information
for tz in tzlist:
  environ['TZ'] = tz 
  txt+=strftime("%H%M")+strftime("%Z")[0]+" "

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
if fs_exists("/proc/acpi/battery/BAT1/"):

  try:
    batinfof = open("/proc/acpi/battery/BAT1/info","r")
    line = " "
    while line:
      line = batinfof.readline()
      if line.find("design capacity:") >= 0:
        dmax = float(line.split()[2])
      elif line.find("last full capacity:") >= 0:
        cmax = float(line.split()[3])

    batinfof.close()
  except:
    dmax = 1.0 
    cmax = 1.0 

  try:
    batstatf = open("/proc/acpi/battery/BAT1/state","r")
    line = " "
    while line:
      line = batstatf.readline()
      if line.find("present rate:") >= 0:
        rate = float(line.split()[2])
      elif line.find("remaining capacity:") >= 0:
        cur = float(line.split()[2])
      elif line.find("charging state:") >= 0:
        bstat = line.split()[2]

    batstatf.close()
  except:
    rate = 1.0
    cur = 1.0
    bstat = "-"

  if bstat == "discharging":
    h = cur/rate
    txt+="-"+str(round((cur/cmax)*100,2))+"%:"+str(round(h,2)).zfill(4)
  elif bstat == "charging":
    h = (cmax-cur)/rate
    txt+="+"+str(round((cur/cmax)*100,2))+"%:"+str(round(h,2)).zfill(4)   #str(int(h))+"."+str(int(60*(h-int(h))))
  elif bstat == "charged":
    txt+="="+str(round((cur/dmax)*100,2))+"%"

## data usage
if fs_exists("/var/local/datausage.dat"):
  try:
    txt+=str(int(float(open("/var/local/datausage.dat","r").readline().split()[2])/1024/500*100))+"%"
  except:
    txt+="?%"

print txt
