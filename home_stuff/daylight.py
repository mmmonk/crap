#!/usr/bin/python

# idea from: http://www.marksdailyapple.com/how-light-affects-our-sleep/

# http://en.wikipedia.org/wiki/Julian_Day
# http://en.wikipedia.org/wiki/Sunrise_equation
# http://pypi.python.org/pypi/astral/

from time import strftime, localtime
from os import stat,execlp
from sys import exit

filename = "/home/case/.daylight"
city = "Amsterdam"

def UpdateFile(sfile,scity):
  import datetime
  from astral import Astral

  a = Astral()
  a.solar_depression = 'civil'
  city = a[scity]
  sun = city.sun(date=datetime.date.today(), local=True)

  ok=1
  try:
    datafile = open(sfile,'w')
  except:
    ok=0

  if ok == 1:
    datafile.write(strftime('%H%M%S',datetime.datetime.timetuple(sun['dawn']))+'\n')
    datafile.write(strftime('%H%M%S',datetime.datetime.timetuple(sun['sunrise']))+'\n')
    datafile.write(strftime('%H%M%S',datetime.datetime.timetuple(sun['noon']))+'\n')
    datafile.write(strftime('%H%M%S',datetime.datetime.timetuple(sun['sunset']))+'\n')
    datafile.write(strftime('%H%M%S',datetime.datetime.timetuple(sun['dusk']))+'\n')
    datafile.close()


if __name__ == "__main__":

  ok=1
  try:
    stats=stat(filename)
  except:
    UpdateFile(filename,city)
    ok=0

  if ok == 1 and int(strftime('%Y%m%d',localtime(stats.st_mtime))) != int(strftime('%Y%m%d')):
    UpdateFile(filename,city)
   
  try:
    datafile = open(filename,'r')
  except:
    sys.exit(1)  

  data = map(lambda x: int(x.rstrip()),datafile.readlines())
  datafile.close() 

  curtime = int(strftime('%H%M%S'))

  xg=["1.3","0.5","0.5"]
  if curtime > data[0]:
    xg=["1","0.7","0.7"]
  if curtime > data[1]:
    xg=["1","1","1.3"]
  if curtime > data[2]:
    xg=["1","1","1"]
  if curtime > data[3]:
    xg=["1","0.7","0.7"]
  if curtime > data[4]:
    xg=["1.3","0.5","0.5"]

  execlp("xgamma","xgamma","-d",":0.0","-q","-rgamma",xg[0],"-ggamma",xg[1],"-bgamma",xg[2])
