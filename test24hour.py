# -*- coding:utf-8 -*-

import os.path
from datetime import datetime

homedir = "/home/pi/WEATHER_STATION_PI/"
now = datetime.now()
dayweathfile =  now.strftime("%d%m%Y") + ".txt"

print(dayweathfile)

if os.path.exists(homedir + dayweathfile):
    print("Day File Exists")
else:
    day = open(homedir + dayweathfile, 'w')
    day.write("testing")
    day.close()
