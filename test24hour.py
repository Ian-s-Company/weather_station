# -*- coding:utf-8 -*-

import os.path
from datetime import datetime



now = datetime.now()
dayweathfile = now.strftime("%d%m%Y") + ".txt"

print(dayweathfile)

if os.path.exists(dayweathfile):
    print("Day File Exists")
else:
    day = open(dayweathfile, "w")
    day.write("testing")
    day.close()
