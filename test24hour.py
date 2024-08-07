# -*- coding:utf-8 -*-

import os.path
from datetime import datetime

APP_DIR = "/opt/weather_station"

now = datetime.now()
dayweathfile = now.strftime("%d%m%Y") + ".txt"

print(dayweathfile)

if os.path.exists(APP_DIR + dayweathfile):
    print("Day File Exists")
else:
    day = open(APP_DIR + dayweathfile, "w")
    day.write("testing")
    day.close()
