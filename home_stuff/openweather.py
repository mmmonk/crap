#!/usr/bin/env python

import urllib
import json
import os
import sys
import time

CITY="Amsterdam"
COUNTRY="NL"
UPDATETIME=3600
URL="http://api.openweathermap.org/data/2.5/weather?q=%s,%s" % (CITY, COUNTRY)
CACHE="/tmp/openweather_cache_%s" % os.environ['USER']

def check_cache():
    try:
        return os.stat(CACHE)[8]
    except OSError:
        return int(time.time()) - UPDATETIME

def read_cache():
    if check_cache() <= int(time.time()) - UPDATETIME:
        write_cache()
    try:
        return json.loads(open(CACHE).read())
    except:
        return None

def write_cache():
    data = get_current_data()
    try:
        open(CACHE,"w").write(json.dumps(data))
    except:
        pass

def get_current_data():
    try:
        return json.loads(urllib.urlopen(URL).read()) 
    except:
        return None

def print_task():
    data = read_cache()
    task = "%s/%sC" % (data['weather'][0]['description'],
            int(data['main']['temp']-273.15))
    return task

def print_full():
    data = read_cache()
    out = ""
    for k,v in sorted(data.iteritems()):
        if type(v) == dict:
            out += "%s\n" % k
            for i,j in sorted(v.iteritems()):
                if "temp" in i:
                    j = j - 273.15
                if i in ['sunrise','sunset']:
                    j = time.asctime(time.localtime(int(j)))
                out += " +-%s: %s\n" % (i,j)
        elif type(v) == list:
            for m in v:
                out += "+\\\n"
                for i,j in sorted(m.iteritems()):
                    out += " +--%s: %s\n" % (i,j)

        else:
            if k in ['dt']:
                v = time.asctime(time.localtime(int(v)))
            out += "%s: %s\n" % (k,v)
    return out

if __name__ == "__main__":

    try:
        arg = sys.argv[1]
    except IndexError:
        arg = None

    if arg:
        if arg == "force":
            write_cache()
            print print_full()
        elif arg == "full":
            print print_full()
        else:
            print print_task()
    else:
        print print_task()
