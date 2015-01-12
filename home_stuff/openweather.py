#!/usr/bin/env python

import urllib
import json
import os
import sys
import time

"""
API: http://openweathermap.org/API
"""

CITY="Amsterdam"
COUNTRY="NL"
UPDATETIME=1800
URL="http://api.openweathermap.org/data/2.5/weather?q=" 
FURL="http://api.openweathermap.org/data/2.5/forecast?q="
CACHE="/tmp/openweather_cache_%s" % os.environ['USER']
FCACHE="/tmp/openweather_forecast_cache_%s" % os.environ['USER']

def beaufort(wind):
    """
    https://en.wikipedia.org/wiki/Beaufort_scale
    """
    if wind >= 32.7:
        return "12 hurricane"
    elif wind > 28.5:
        return "11 violent storm"
    elif wind > 24.5:
        return "10 violent storm"
    elif wind > 28.5:
        return "9 violent storm"
    elif wind > 17.2:
        return "8 gale"
    elif wind > 13.9:
        return "7 high wind"
    elif wind > 10.8:
        return "6 strong breeze"
    elif wind > 8.0:
        return "5 fresh breeze"
    elif wind > 5.5:
        return "4 modere breeze"
    elif wind > 3.4:
        return "3 gentle breeze"
    elif wind > 1.6:
        return "2 light breeze"
    elif wind > 0.3:
        return "1 light air"
    else:
        return "0 calm"

def check_cache(cache_file, updatetime=1800):
    try:
        return os.stat(cache_file)[8]
    except OSError:
        return int(time.time()) - updatetime 

def read_cache(cache_file, updatetime=1800):
    if check_cache(cache_file) <= int(time.time()) - updatetime:
        return {}
    try:
        return json.loads(open(cache_file).read())
    except:
        return {}

def write_cache(cache_file, data):
    try:
        open(cache_file,"w").write(json.dumps(data))
    except:
        pass

def get_json_url(url):
    try:
        return json.loads(urllib.urlopen(url).read()) 
    except:
        return None

def get_current_data():
    try:
        return get_json_url("%s%s,%s" % (URL,CITY,COUNTRY))
    except:
        return None

def get_forecast_data():
    try:
        return get_json_url("%s%s,%s" % (FURL,CITY,COUNTRY))
    except:
        return None

def current_weather(cache_file):
    data = read_cache(cache_file)
    if not data:
        data = get_current_data()
        if data:
            write_cache(cache_file, data)
    if data:
        weather = data['weather'][0]['description']
        temp = round(data['main']['temp']-273.15,1)
        wind = data['wind']['speed']

        task = "%s/%sC" % (weather, temp)
        if float(wind) > 10:
            if data['wind'].has_key('gust'):
                wind = "%s/%s" % (wind,data['wind']['gust'])
            task += "/%s" % (wind)
        return task
    else:
        return ""

def current_weather_full(cache_file):
    data = read_cache(cache_file)
    if not data:
        data = get_current_data()
        if data:
            write_cache(cache_file, data)
    out = ""
    if data:
        for k,v in sorted(data.iteritems()):
            if type(v) == dict:
                out += "%s\n" % k
                for i,j in sorted(v.iteritems()):
                    if "temp" in i:
                        j = j - 273.15
                    if i in ['sunrise','sunset']:
                        j = time.asctime(time.localtime(int(j)))
                    if 'wind' in k and 'speed' in i:
                        j = "%s (%s)" % (beaufort(j), j)
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

def weather_forecast(cache_file):
    data = read_cache(cache_file)
    if not data:
        data = get_forecast_data()
        if data:
            write_cache(cache_file, data)
    out = ""
    if data:
        for day in data['list']:
            dt = time.asctime(time.localtime(int(day['dt'])))
            wind = "%s (%s)" % (beaufort(day['wind']['speed']),\
                day['wind']['speed'])
            desc = day['weather'][0]['description']
            temp = round(day['main']['temp'] - 273.15,1)
            out += "%s: %s / %sC / %s\n" % (dt, desc, temp, wind)
    return out

if __name__ == "__main__":
#    import argparse
#
#    p = argparse.ArgumentParser(description='Openweather client')
#    p.add_argument('-f',action='store_true',
#            help="force downloading of new data, refresh cache")
#    p.add_argument('--city',help="the cli challenge (DEC), output of: cli challenge generate")
#    args = p.parse_args()
    try:
        arg = sys.argv[1]
    except IndexError:
        arg = None

    if arg:
        if arg == "force":
            data = get_current_data()
            if data:
                write_cache(CACHE, data)
            data = get_forecast_data()
            if data:
                write_cache(FCACHE, data)
        elif arg == "full":
            print current_weather_full(CACHE)
        elif arg == "forecast":
            print weather_forecast(FCACHE)
        else:
            print current_weather(CACHE)
    else:
        print current_weather(CACHE)
