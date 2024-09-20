import time
import requests
import locale


# import os.path
import logging
from os import path
from PIL import Image

locale.setlocale(locale.LC_TIME, "")


class Weather:
    def __init__(self, latitude, longitude, api_id, app_dir="/opt/weather_station"):
        self.latitude = latitude
        self.longitude = longitude
        self.api_key = api_id
        self.app_dir = app_dir
        self.max_lvl_pollution = {
            "co": 10000,
            "no": 30,
            "no2": 40,
            "o3": 120,
            "so2": 50,
            "pm2_5": 20,
            "pm10": 30,
            "nh3": 100,
        }
        self.prevision = [0, [[0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0], [0, 0]]]

    def update_pol(self):
        pollution_url = (
            "https://api.openweathermap.org/data/2.5/air_pollution?lat="
            + self.latitude
            + "&lon="
            + self.longitude
            + "&lang=en&appid="
            + self.api_key
        )
        got_data = False
        logging.info("-------Pollution Update Begin ")
        while got_data == False:
            logging.info("Checking Pollution URL Status")
            try:
                self.pol_data = requests.get(pollution_url, timeout=30)
            except:
                time.sleep(60)
                continue

            if self.pol_data.ok:
                logging.info(self.pol_data.status_code)
                got_data = True
                logging.info("Got data from Pollution URL to return successfully")
                self.pol_data = self.pol_data.json()
            else:
                logging.info("Waiting for the Pollution URL to return successfully")
                time.sleep(15)
                self.pol_data = None
        logging.info("-------Pollution Update End ")

        return self.pol_data

    def update(self):
        weather_url = (
            "https://api.openweathermap.org/data/2.5/onecall?lat="
            + self.latitude
            + "&lon="
            + self.longitude
            + "&lang=en&appid="
            + self.api_key
            + "&units=imperial"
        )
        got_data = False
        logging.info("-------Weather Update Begin ")
        while got_data == False:
            logging.info("Checking Weather URL Status")
            try:
                self.weather_data = requests.get(weather_url, timeout=30)
            except:
                time.sleep(60)
                continue

            if self.weather_data.ok:
                logging.info(self.weather_data.status_code)
                got_data = True
                logging.info("Got data from Weather URL to return successfully")
                self.data = self.weather_data.json()
            else:
                logging.info("Waiting for the Weather URL to return successfully")
                time.sleep(15)
                self.data = None
        logging.info("-------Weather Update End ")

        return self.data

    def get_current(self):
        return self.data["current"]

    def get_daily(self, day):
        return self.data["daily"][day]

    def get_daily_all(self):
        return self.data["daily"]

    def get_hourly(self, hour=None, max=0):
        if hour != None:
            return self.data["hourly"][hour]
        else:
            if max != 0:
                i = 0
                hourly_data = []
                for hour in self.data["hourly"]:
                    if i < max:
                        hourly_data.append(hour)
                        i = i + 1
                    else:
                        continue
                return hourly_data
            else:
                return self.data["hourly"]

    def get_weather(self, time_span_data):
        weather = time_span_data["weather"][0]
        return weather

    def current_time(self):
        return time.strftime(
            "%b %-d %Y at %I:%M", time.localtime(self.data["current"]["dt"])
        )

    def current_temp(self):
        return "{:.0f}".format(self.data["current"]["temp"])

    def current_uvi(self):
        return "{:.0f}".format(self.data["current"]["uvi"])

    def current_dew_point(self):
        return "{:.0f}".format(self.data["current"]["dew_point"])

    def current_pressure(self):
        return "{:.0f}".format(self.data["current"]["pressure"])

    def current_feelslike(self):
        return "{:.0f}".format(self.data["current"]["feels_like"])

    def current_daymax(self):
        return "{:.0f}".format(self.data["daily"][0]["temp"]["max"])

    def current_daymin(self):
        return "{:.0f}".format(self.data["daily"][0]["temp"]["min"])

    def current_hum(self):
        return "{:.0f}".format(self.data["current"]["humidity"]) + "%"

    def current_cloud_cov(self):
        return "{:.0f}".format(self.data["current"]["clouds"]) + "%"

    def current_sunrise(self):
        return time.strftime("%H:%M", time.localtime(self.data["current"]["sunrise"]))

    def current_sunset(self):
        return time.strftime("%H:%M", time.localtime(self.data["current"]["sunset"]))

    def wind_dir(self, wind_dir_deg):
        if wind_dir_deg < 11 or wind_dir_deg >= 349:
            direction = "N"
        elif 12 <= wind_dir_deg < 34:
            direction = "NNE"
        elif 35 <= wind_dir_deg < 57:
            direction = "NE"
        elif 58 <= wind_dir_deg < 80:
            direction = "ENE"
        elif 81 <= wind_dir_deg < 101:
            direction = "E"
        elif 102 <= wind_dir_deg < 122:
            direction = "ESE"
        elif 123 <= wind_dir_deg < 145:
            direction = "SE"
        elif 146 <= wind_dir_deg < 168:
            direction = "SSE"
        elif 169 <= wind_dir_deg < 192:
            direction = "S"
        elif 193 <= wind_dir_deg < 215:
            direction = "SSW"
        elif 216 <= wind_dir_deg < 238:
            direction = "SW"
        elif 239 <= wind_dir_deg < 262:
            direction = "WSW"
        elif 263 <= wind_dir_deg < 281:
            direction = "W"
        elif 282 <= wind_dir_deg < 303:
            direction = "WNW"
        elif 304 <= wind_dir_deg < 326:
            direction = "NW"
        elif 327 <= wind_dir_deg < 349:
            direction = "NNW"
        else:
            direction = "N/A"
        return direction, wind_dir_deg

    def current_weather(self):
        description = self.data["current"]["weather"][0]["id"]
        return description

    def curent_wind_deg(self):
        description = self.data["current"]["wind_deg"]
        return description

    def current_condition(self):
        description = self.data["current"]["weather"][0]["description"]
        return description

    def rain_next_hour(self):
        input_minutely = self.data["minutely"]
        rain = []
        rain_next_hour = [
            ["+10'", 0],
            ["+20'", 0],
            ["+30'", 0],
            ["+40'", 0],
            ["+50'", 0],
            ["+1h", 0],
        ]
        for i in range(len(input_minutely)):
            rain.append(input_minutely[i]["precipitation"])
        for i in range(6):
            rain_next_hour[i][1] = sum(rain[i * 10 + 1 : i * 10 + 10])
        return rain_next_hour

    def hourly_forecast(self):
        hourly = {
            "+3h": {"temp": "", "pop": "", "id": ""},
            "+6h": {"temp": "", "pop": "", "id": ""},
            "+12h": {"temp": "", "pop": "", "id": ""},
        }
        # Forecast +3h
        hourly["+3h"]["temp"] = "{:.0f}".format(self.data["hourly"][3]["temp"])
        hourly["+3h"]["pop"] = (
            "{:.0f}".format(self.data["hourly"][3]["pop"] * 100) + "%"
        )
        hourly["+3h"]["id"] = self.data["hourly"][3]["weather"][0]["id"]
        # Forecast +3h
        hourly["+6h"]["temp"] = "{:.0f}".format(self.data["hourly"][6]["temp"])
        hourly["+6h"]["pop"] = (
            "{:.0f}".format(self.data["hourly"][6]["pop"] * 100) + "%"
        )
        hourly["+6h"]["id"] = self.data["hourly"][6]["weather"][0]["id"]
        # Forecast +3h
        hourly["+12h"]["temp"] = "{:.0f}".format(self.data["hourly"][12]["temp"])
        hourly["+12h"]["pop"] = (
            "{:.0f}".format(self.data["hourly"][12]["pop"] * 100) + "%"
        )
        hourly["+12h"]["id"] = self.data["hourly"][12]["weather"][0]["id"]

        return hourly

    def daily_forecast(self):
        daily = {
            "+24h": {"date": "", "min": "", "max": "", "pop": "", "id": ""},
            "+48h": {"date": "", "min": "", "max": "", "pop": "", "id": ""},
            "+72h": {"date": "", "min": "", "max": "", "pop": "", "id": ""},
            "+96h": {"date": "", "min": "", "max": "", "pop": "", "id": ""},
        }
        i = 1
        for key in daily.keys():
            daily[key]["date"] = time.strftime(
                "%A", time.localtime(self.data["daily"][i]["dt"])
            )
            daily[key]["min"] = "{:.0f}".format(self.data["daily"][i]["temp"]["min"])
            daily[key]["max"] = "{:.0f}".format(self.data["daily"][i]["temp"]["max"])
            daily[key]["pop"] = (
                "{:.0f}".format(self.data["daily"][i]["pop"] * 100) + "%"
            )
            daily[key]["id"] = self.data["daily"][i]["weather"][0]["id"]
            i += 1

        return daily

    # def my_daily_forecast(self):
    #    daily_forecast_info
    #    for day in self.data['daily]:

    def graph_p_t(self):
        if self.prevision[0] != self.data["daily"][0]["dt"]:
            self.prevision[0] = self.data["daily"][0]["dt"]
            self.prevision = [self.prevision[0], self.prevision[1][1:]]
            self.prevision[1].append(
                [
                    self.data["daily"][0]["pressure"],
                    round(self.data["daily"][0]["temp"]["day"], 0),
                ]
            )

    def get_icon(self, icon):
        icon_dir = self.app_dir + "/downloaded_icons/"
        icon_jpg = icon_dir + str(icon) + ".jpg"
        icon_png = str(icon) + ".png"
        if not path.exists(icon_jpg):
            icon_updated_png = str(icon) + "-updated.png"
            url = "https://openweathermap.org/img/wn/" + icon_png
            icon_response = requests.get(
                url, allow_redirects=True, stream=True, timeout=30
            )
            icon_png = icon_dir + str(icon) + ".png"
            open(icon_png, "wb").write(icon_response.content)
            img = Image.open(icon_png)  # .convert("LA")
            img = img.crop((8, 8, 42, 42))

            bg = Image.new("RGB", img.size, (255, 255, 255))
            bg.paste(img, (0, 0), img)
            bg.save(icon_dir + str(icon) + "-updated.png", "PNG")
            img_updated = Image.open(icon_dir + icon_updated_png).convert("L")
            newimdata = []
            for color in img_updated.getdata():
                if color == 255:
                    newimdata.append(255)
                if color < 255 and color >= 191:
                    newimdata.append(191)
                elif color < 191 and color >= 127:
                    newimdata.append(127)
                elif color < 127 and color >= 63:
                    newimdata.append(63)
                elif color < 63 and color >= 0:
                    newimdata.append(0)
            newim = Image.new(img_updated.mode, img_updated.size)
            newim.putdata(newimdata)
            newim.save(icon_jpg)
        return icon_jpg

    def weather_description(self, id):
        icon = "sun"
        weather_detail = "good weather"
        if id // 100 != 8:
            id = id // 100
            if id == 2:
                icon = "thunder"
                weather_detail = "Thunderstorm"
            elif id == 3:
                icon = "drizzle"
                weather_detail = "Drizzle"
            elif id == 5:
                icon = "rain"
                weather_detail = "Rain"
            elif id == 6:
                icon = "snow"
                weather_detail = "Snow"
            elif id == 7:
                icon = "atm"
                weather_detail = "Fog"
            else:
                weather_detail = "Error"
        else:
            if id == 801:
                icon = "25_clouds"
                weather_detail = "Partly Cloudy"
            elif id == 802:
                icon = "50_clouds"
                weather_detail = "Cloudy"
            elif id == 803 or id == 804:
                icon = "100_clouds"
                weather_detail = "Covered"

        return icon, weather_detail

    def alert(self):
        try:
            alert_descrip = self.data["alerts"][0]["event"]
        except:
            alert_descrip = 0
        return alert_descrip

    def co(self):  # Carbon Monoxide
        if 0 < self.pol_data["list"][0]["components"]["co"] < 4400:
            status = "good"
        elif 4400 < self.pol_data["list"][0]["components"]["co"] < 9400:
            status = "fair"
        elif 9400 < self.pol_data["list"][0]["components"]["co"] < 12400:
            status = "moderate"
        elif 12400 < self.pol_data["list"][0]["components"]["co"] < 15400:
            status = "poor"
        elif 15400 < self.pol_data["list"][0]["components"]["co"]:
            status = "very poor"

        return self.pol_data["list"][0]["components"]["co"], status

    def no(self):  # Nitrogen Monoxide
        return self.pol_data["list"][0]["components"]["no"]

    def no2(self):  # Nitrogen Dioxide
        if 0 < self.pol_data["list"][0]["components"]["no2"] < 40:
            status = "good"
        elif 40 < self.pol_data["list"][0]["components"]["no2"] < 70:
            status = "fair"
        elif 70 < self.pol_data["list"][0]["components"]["no2"] < 150:
            status = "moderate"
        elif 150 < self.pol_data["list"][0]["components"]["no2"] < 200:
            status = "poor"
        elif 200 < self.pol_data["list"][0]["components"]["no2"]:
            status = "very poor"

        return self.pol_data["list"][0]["components"]["no2"], status

    def o3(self):  # Ozone
        if 0 < self.pol_data["list"][0]["components"]["o3"] < 60:
            status = "good"
        elif 60 < self.pol_data["list"][0]["components"]["o3"] < 100:
            status = "fair"
        elif 100 < self.pol_data["list"][0]["components"]["o3"] < 140:
            status = "moderate"
        elif 140 < self.pol_data["list"][0]["components"]["o3"] < 180:
            status = "poor"
        elif 180 < self.pol_data["list"][0]["components"]["o3"]:
            status = "very poor"

        return self.pol_data["list"][0]["components"]["o3"], status

    def so2(self):  # Sulpher Dioxide
        if 0 < self.pol_data["list"][0]["components"]["so2"] < 20:
            status = "good"
        elif 20 < self.pol_data["list"][0]["components"]["so2"] < 80:
            status = "fair"
        elif 80 < self.pol_data["list"][0]["components"]["so2"] < 250:
            status = "moderate"
        elif 250 < self.pol_data["list"][0]["components"]["so2"] < 350:
            status = "poor"
        elif 350 < self.pol_data["list"][0]["components"]["so2"]:
            status = "very poor"

        return self.pol_data["list"][0]["components"]["so2"], status

    def pm2_5(self):
        return self.pol_data["list"][0]["components"]["pm2_5"]

    def pm10(self):
        return self.pol_data["list"][0]["components"]["pm10"]

    def nh3(self):  # Ammonia
        return self.pol_data["list"][0]["components"]["nh3"]
