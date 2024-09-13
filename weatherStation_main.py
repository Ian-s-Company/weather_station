# -*- coding: utf-8 -*-

from weather import *
from news import *
from display import *
import json
import sys
from datetime import datetime
from PIL import Image, ImageDraw
from gpiozero import Button  # Pins 5,6,13,19
import logging
import os.path
import argparse
import configparser

config = configparser.ConfigParser()
config.sections()


# Add the arguments to the parser

ap = argparse.ArgumentParser(description="Get Weather Display Args.")
ap.add_argument("-c", "--config", required=False, help="Config File")
ap.add_argument(
    "-a",
    "--app_dir",
    required=False,
    help="application directory default is /opt/weather_station",
    default="/opt/weather_station",
    type=str,
)
ap.add_argument("-w", "--weatherapikey", required=False, help="Key for OpenWeather API")
ap.add_argument(
    "-n",
    "--newsapikey",
    required=False,
    help="Key for News API (from the Washing Post as the default)",
    type=str,
)
ap.add_argument(
    "-s",
    "--screensize",
    required=False,
    help="Options are 7x5in (800x600) and 2.7in (176x264)",
    default="2.7in",
    type=str,
)
ap.add_argument(
    "-l", "--lat", required=False, help="Lattitude", default="33.104191", type=str
)
ap.add_argument(
    "-g", "--long", required=False, help="Longitude", default="-96.671738", type=str
)
ap.add_argument(
    "-d",
    "--debug",
    required=False,
    help="Debug for Deployment",
    action="store_true",
)

args = vars(ap.parse_args())

config_file = args["config"]
if config_file != None:
    if os.path.exists(config_file):
        config.read(config_file)
        app_dir = config["DEFAULT"]["APP_DIR"]
        api_key_weather = config["DEFAULT"]["WEATHER_API_KEY"]
        api_key_news = config["DEFAULT"]["NEWS_API_KEY"]
        screen_size = config["DEFAULT"]["SCREEN_SIZE"]
        lat = config["DEFAULT"]["LATTITUDE"]
        lon = config["DEFAULT"]["LONGITUDE"]
        debug = config["DEFAULT"].get("DEBUG")
    else:
        # print("Config file could not be found")
        exit(22)
else:
    # print("No config file specified")
    app_dir = str(args["app_dir"])
    api_key_weather = str(args["weatherapikey"])
    api_key_news = str(args["newsapikey"])
    screen_size = str(args["screensize"])
    lat = str(args["lat"])
    lon = str(args["long"])
    debug = args["debug"]

search_text = "<APP_DIR>"
with open(app_dir + "/weatherstation.service", "r") as file:
    data = file.read()
    data = data.replace(search_text, app_dir)
with open(app_dir + "/weatherstation.service", "w") as file:
    file.write(data)

logger = logging.getLogger(__name__)
logging.basicConfig(filename=app_dir + "/weatherStation.log", level=logging.DEBUG)

if screen_size == "7x5in":
    logger.info("Screen size is 7x5in")
    news_width = 340
    import epd7in5b_V2
elif screen_size == "2.7in":
    logger.info("Screen size is 2in7")
    news_width = 170
    import epd2in7
else:
    pass


def map_resize(val, in_mini, in_maxi, out_mini, out_maxi):
    if in_maxi - in_mini != 0:
        out_temp = (val - in_mini) * (out_maxi - out_mini) // (
            in_maxi - in_mini
        ) + out_mini
    else:
        out_temp = out_mini
    return out_temp


class weather_station:
    def __init__(self, epd, weather, news):
        self.epd = epd
        self.weather = weather
        self.news = news
        self.epd.init()
        self.weather.update()
        self.weather.update_pol()
        self.news_updates = self.news.update()
        # self.epd.Clear(0xFF)

    def get_news_footer(self, draw):
        news_selected = self.news.selected_title(self.news_updates)
        draw.text((0, 155), "News: ", fill=0, font=font12)
        draw.text((38, 155), news_selected[0][0], fill=0, font=font12)
        draw.line((0, 154, 264, 154), fill=0, width=1)  # HORIZONTAL SEPARATION
        return draw

    def get_date_header(self, draw):
        draw.text((0, 0), self.weather.current_time(), fill=0, font=font12)
        draw.line((0, 15, 264, 15), fill=0, width=1)  # HORIZONTAL SEPARATION
        return draw

    def epd_initialize(self):
        self.epd.init()
        self.epd.Clear()
        Himage = Image.new(
            "1", (self.epd.height, self.epd.width), 255
        )  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        return (draw, Himage)
    
    def epd_finish(self):
        self.epd.sleep()
        
    def button2(self):  # Hourly Forecast
        logger.info("Drawing Hourly Forecast")
        draw, Himage = self.epd_initialize()
        draw = self.get_date_header(draw)
        time = "hour"
        hour_pixel_array = [
            [0, 16],
            [66, 16],
            [132, 16],
            [198, 16],
            [0, 97],
            [66, 97],
            [132, 97],
            [198, 97],
        ]
        hour_span = 3
        i = 0
        for start_pixel in hour_pixel_array:
            hour_info = self.forecast(time, i)
            draw, icon = self.hour_summary(draw, hour_info, start_pixel)
            Himage.paste(icon, (start_pixel[0], start_pixel[1] + 13))
            i = i + hour_span
        self.epd.display(self.epd.getbuffer(Himage))
        self.epd_finish()
        return 0

    def button3(self):  # Daily Forecast
        logger.info("Drawing Daily Forecast")
        draw, Himage = self.epd_initialize()
        draw = self.get_date_header(draw)
        start_pixel = [0, 16]
        time = "day"
        day_pixel_array = [
            [0, 16],
            [66, 16],
            [132, 16],
            [198, 16],
            [0, 98],
            [66, 98],
            [132, 98],
            [198, 98],
        ]
        i = 0
        for start_pixel in day_pixel_array:
            day_info = self.forecast(time, i)
            draw, icon = self.day_summary(draw, day_info, start_pixel)
            Himage.paste(icon, (start_pixel[0], start_pixel[1] + 13))
            i = i + 1
        self.epd.display(self.epd.getbuffer(Himage))
        self.epd_finish()
        return 0

    def button5(self):  # Pollution and other Metrics 
        logger.info("Drawing Button 5 screen")
        draw, Himage = self.epd_initialize()
        draw = self.get_news_footer(draw)
        draw = self.get_date_header(draw)
        day_high_temps = {}
        day_low_temps = {}
        daily_all = self.weather.get_daily_all()
        co_num, co_status = self.weather.co()
        draw.text((127, 20), "CO (\u03BCg/m\u00b3)", fill=0, font=font12)
        draw.text((127, 30), str(co_status.upper() + " (" + str(co_num) + ")"), fill=0, font=font20)
        so2_num, so2_status = self.weather.so2()
        draw.text((127, 50), "SO2 (\u03BCg/m\u00b3)", fill=0, font=font12)
        draw.text((127, 60), str(so2_status.upper() + " (" + str(so2_num) + ")"), fill=0, font=font16)
        no2_num, no2_status = self.weather.no2()
        draw.text((127, 80), "NO2 (\u03BCg/m\u00b3)", fill=0, font=font12)
        draw.text((127, 90), str(no2_status.upper() + " (" + str(no2_num) + ")") , fill=0, font=font20)
        o3_num, o3_status = self.weather.o3()
        draw.text((127, 110), "Ozone (\u03BCg/m\u00b3)", fill=0, font=font12)
        draw.text((127, 120), str(o3_status + " (" + str(o3_num) + ")"), fill=0, font=font20)
        draw.text((2, 20), "Cloud %", fill=0, font=font12)
        draw.text(
            (2, 30), str(self.weather.current_cloud_cov()), fill=0, font=font20
        )  # CLOUD COVER
        draw.text((2, 50), "UVI Index", fill=0, font=font12)
        draw.text((2, 60), str(self.weather.current_uvi()), fill=0, font=font20)  # UVI
        draw.text((2, 80), "Dew Point", fill=0, font=font12)
        draw.text(
            (2, 90), str(self.weather.current_dew_point() + str("\xb0")), fill=0, font=font20
        )  # Dew Point
        draw.text((2, 110), "Pressure (hPa)", fill=0, font=font12)
        draw.text(
            (2, 120), str(self.weather.current_pressure()), fill=0, font=font20
        )  # Pressure
        self.epd.display(self.epd.getbuffer(Himage))
        self.epd_finish()
        return 0

    def button6(self):  # Daily High/Low Graph
        logger.info("Drawing Button 5 screen")
        draw, Himage = self.epd_initialize()
        daily_all = self.weather.get_daily_all()
        draw = self.data_graph(
            self.weather,
            draw,
            daily_all,
            '["temp"]["max"]',
            [150, 240],
            [5, 5],
            point_label_position="top",
            x_label="day",
            title="Daily High/Low",
        )
        draw = self.data_graph(
            self.weather,
            draw,
            daily_all,
            '["temp"]["min"]',
            [150, 240],
            [5, 5],
            point_label_position="bottom",
        )
        self.epd.display(self.epd.getbuffer(Himage))
        self.epd_finish()
        return 0

    def data_graph(
        self,
        weather,
        draw,
        weather_data,
        weather_metric,
        graph_dim,  # size of Graph
        start_pixel,
        fill_col="black",
        point_label_position=None,
        x_label=None,
        title="",
    ):  # weather data is array of data, elements is the data field to be graphed
        corner = [start_pixel[0], start_pixel[1] + graph_dim[0]]

        draw.line(
            (
                start_pixel[0],
                start_pixel[1] + graph_dim[0],
                start_pixel[0] + graph_dim[1],
                start_pixel[1] + graph_dim[0],
            ),
            fill=0,
            width=1,
        )  # HORIZONTAL LINE
        draw.line(
            (
                start_pixel[0],
                start_pixel[1],
                start_pixel[0],
                start_pixel[1] + graph_dim[0],
            ),
            fill=0,
            width=1,
        )  # VERTICAL LINE
        pixel_spacing = int(graph_dim[1] / len(weather_data))

        dot_size = 2
        iter = 0
        last_start_h = 0
        last_start_v = 0
        date_string = datetime.fromtimestamp(weather_data[0]["dt"])
        short_date = date_string.strftime("%D")
        for j in weather_data:
            logger.info("The entry for this datapoint is " + str(j))
            timestamp = j["dt"]
            weather_data = eval(str(j) + weather_metric)
            logger.info("The weather_data for this datapoint is " + str(weather_data))
            logger.info("Corner is: " + str(corner))
            logger.info("Pixel Spacing is: " + str(pixel_spacing))
            logger.info("Iteration is: " + str(iter))

            start_h = corner[0] - dot_size + round((pixel_spacing * (iter + 0.5)))
            start_v = corner[1] - dot_size - round(weather_data)
            finish_h = corner[0] + dot_size + round((pixel_spacing * (iter + 0.5)))
            finish_v = corner[1] + dot_size - round(weather_data)

            logger.info("Start Horizontal: " + str(start_h))
            logger.info("Finish Horizontal: " + str(finish_h))
            logger.info("Start Vertical: " + str(start_v))
            logger.info("Finish Vertical: " + str(finish_v))

            draw.ellipse(
                (round(start_h), round(start_v), round(finish_h), round(finish_v)),
                fill=fill_col,
            )  # Drawing Data Point

            if point_label_position == "top":
                label_position = finish_v - dot_size - 18
            elif point_label_position == "bottom":
                label_position = finish_v + dot_size + 1
            else:
                label_position = finish_v + dot_size

            draw.text(
                (round(start_h - 6), label_position),
                str(round(weather_data)),
                fill=0,
                font=font12,
            )

            date_string = datetime.fromtimestamp(timestamp)
            if x_label == "day":
                short_day = date_string.strftime("%a")
                draw.text(
                    (round(start_h - 6), corner[1]), short_day, fill=0, font=font12
                )
            if last_start_h != 0:
                draw.line(
                    (
                        last_start_h + (dot_size / 2),
                        last_start_v - (dot_size / 2),
                        (finish_h + start_h) / 2,
                        (finish_v + start_v) / 2,
                    ),
                    fill=0,
                    width=1,
                )
            last_start_h = (start_h + finish_h) / 2
            last_start_v = (start_v + finish_v) / 2
            iter = iter + 1
        draw.text(
            (corner[0] + round(graph_dim[1] / 2) - 60, start_pixel[1]),
            title,
            fill=0,
            font=font16,
        )
        draw.text(
            (8, 4),
            short_date,
            fill=0,
            font=font12,
        )
        return draw

    def forecast(self, day_or_hour, no_of_time):
        if day_or_hour == "day":
            weather_info = self.weather.get_daily(no_of_time)
            name = datetime.fromtimestamp(weather_info["dt"]).strftime("%A")
            high = round(weather_info["temp"]["max"])
            low = round(weather_info["temp"]["min"])
        elif day_or_hour == "hour":
            weather_info = self.weather.get_hourly(no_of_time)
            name = datetime.fromtimestamp(weather_info["dt"]).strftime("%H:%M")
            high = round(weather_info["temp"])
            low = round(weather_info["feels_like"])
        icon_list = []
        for i in weather_info["weather"]:
            icon = self.weather.get_icon(i["icon"])
            icon_list.append(icon)
        icon = icon_list[0]
        detail = weather_info["weather"][0]["description"]
        pop = str(round(weather_info["pop"] * 100))
        if "rain" in weather_info:
            if day_or_hour == "hour":
                rain = weather_info["rain"]["1h"]
            elif day_or_hour == "day":
                rain = weather_info["rain"]
            rain = round(rain)
            rain = str(rain)
        else:
            rain = 0
        w_spd = round(weather_info["wind_speed"])
        w_dir = round(weather_info["wind_deg"])
        return icon, detail, high, low, name, pop, rain, w_spd, w_dir

    def day_summary(self, draw, day_info, start_pixel):
        draw.text(
            (start_pixel[0], start_pixel[1]), day_info[4], fill=0, font=font12
        )  # DAY NAME
        draw.text(
            (start_pixel[0] + 35, start_pixel[1] + 12),
            str(day_info[2]) + str("\xb0"),
            fill=0,
            font=font16,
        )  # DAY HIGH
        draw.text(
            (start_pixel[0] + 35, start_pixel[1] + 35),
            str(day_info[3])+ str("\xb0"),
            fill=0,
            font=font16,
        )  # DAY LOW
        draw.text(
            (start_pixel[0], start_pixel[1] + 53),
            str(day_info[5]) + "% " + str(day_info[6]),
            fill=0,
            font=font12,
        )
        draw.text(
            (start_pixel[0], start_pixel[1] + 63),
            str(day_info[7]) + "mph " + self.weather.wind_dir(day_info[8]),
            fill=0,
            font=font12,
        )
        icon = Image.open(day_info[0])
        icon = icon.resize((30, 30))
        return draw, icon

    def day_summary_large(self, draw, day_info, start_pixel):
        draw.text(
            (start_pixel[0], start_pixel[1]), day_info[4], fill=0, font=font12
        )  # DAY NAME
        draw.text(
            (start_pixel[0] + 5, start_pixel[1] + 60),
            str(day_info[2])
            + "\N{DEGREE SIGN}/"
            + str(day_info[3])
            + "\N{DEGREE SIGN}",
            fill=0,
            font=font20,
        )  # DAY HIGH/LOW
        draw.text(
            (start_pixel[0], start_pixel[1] + 85),
            str(day_info[5]) + "% " + str(day_info[6]),
            fill=0,
            font=font16,
        )
        draw.text(
            (start_pixel[0], start_pixel[1] + 101),
            str(day_info[7]) + "mph " + self.weather.wind_dir(day_info[8]),
            fill=0,
            font=font16,
        )
        icon = Image.open(day_info[0])
        icon = icon.resize((45, 45))
        return draw, icon

    def hour_summary(self, draw, hour_info, start_pixel):
        draw.text(
            (start_pixel[0], start_pixel[1]), hour_info[4], fill=0, font=font12
        )  # HOUR
        draw.text(
            (start_pixel[0] + 35, start_pixel[1] + 15),
            str(hour_info[2])+ str("\xb0"),
            fill=0,
            font=font16,
        )  # HOUR TEMP
        draw.text(
            (start_pixel[0], start_pixel[1] + 53),
            str(hour_info[5]) + "% " + str(hour_info[6]),
            fill=0,
            font=font12,
        )
        draw.text(
            (start_pixel[0], start_pixel[1] + 65),
            str(hour_info[7]) + "mph " + self.weather.wind_dir(hour_info[8]),
            fill=0,
            font=font12,
        )
        icon = Image.open(hour_info[0])
        icon = icon.resize((30, 30))
        return draw, icon

    def hour_summary_large(self, draw, hour_info, start_pixel):
        draw.text(
            (start_pixel[0] + 15, start_pixel[1]), hour_info[4], fill=0, font=font16
        )  # HOUR
        draw.text(
            (start_pixel[0] + 5, start_pixel[1] + 60),
            str(hour_info[2])
            + "\N{DEGREE SIGN}/"
            + str(hour_info[3])
            + "\N{DEGREE SIGN}",
            fill=0,
            font=font20,
        )  # HOUR FEELS LIKE
        draw.text(
            (start_pixel[0], start_pixel[1] + 85),
            str(hour_info[5]) + "% " + str(hour_info[6]),
            fill=0,
            font=font16,
        )
        draw.text(
            (start_pixel[0], start_pixel[1] + 105),
            str(hour_info[7]) + "mph " + self.weather.wind_dir(hour_info[8]),
            fill=0,
            font=font16,
        )
        icon = Image.open(hour_info[0])
        icon = icon.resize((45, 45))
        return draw, icon

    def button1(self):  # Home Button
        logger.info("Drawing Button 1 screen")
        draw, Himage = self.epd_initialize()
        draw = self.get_date_header(draw)
        current_info = self.weather.get_current()
        logger.info(
            "Begin update @"
            + self.weather.current_time()
            + " at latitude "
            + lat
            + " longitude "
            + lon
        )

        day_info = self.weather.get_daily(0)
        hour_info = self.weather.get_hourly(0)
        sunrise_icon = Image.open(app_dir + "/static_icons/sunrise.bmp")
        sunrise_icon = sunrise_icon.resize((30, 30))
        sunset_icon = Image.open(app_dir + "/static_icons/sunset.bmp")
        sunset_icon = sunset_icon.resize((30, 30))
        Himage.paste(sunrise_icon, (225, 20))
        Himage.paste(sunset_icon, (225, 60))

        draw = ImageDraw.Draw(Himage)
        draw = self.get_news_footer(draw)
        draw = self.get_date_header(draw)

        icon_list = []
        for i in current_info["weather"]:
            icon = self.weather.get_icon(i["icon"])
            icon_list.append(icon)
            # cur_condition = self.weather.weather_description(self.weather.current_weather())[1]
        if len(icon_list) == 2:
            cur_icon_name1 = icon_list[0]
            cur_icon_name2 = icon_list[1]
            cur_icon1 = Image.open(cur_icon_name1)  # .convert('LA')
            cur_icon2 = Image.open(cur_icon_name2)  # .convert('LA')
            cur_icon1 = cur_icon1.resize((30, 30), None, None, 3)
            cur_icon2 = cur_icon2.resize((30, 30), None, None, 3)
            Himage.paste(cur_icon1, (120, 90))
            Himage.paste(cur_icon2, (120, 120))
        elif len(icon_list) == 1:
            cur_icon_name1 = icon_list[0]
            cur_icon1 = Image.open(cur_icon_name1)  # .convert('LA')
            cur_icon1 = cur_icon1.resize((40, 40), None, None, 3)
            Himage.paste(cur_icon1, (100, 100))
        draw.text(
            (165, 28), self.weather.current_sunrise(), fill=0, font=font20
        )  # SUNRISE TIME
        draw.text(
            (165, 63), self.weather.current_sunset(), fill=0, font=font20
        )  # SUNSET TIME
        draw.text((165, 85), "Humidity", fill=0, font=font12)
        draw.text(
            (165, 95), str(current_info["humidity"]) + "%", fill=0, font=font20
        )  # HUMIDTY
        draw.text(
            (0, 25),
            self.weather.weather_description(self.weather.current_weather())[1].upper(),
            fill=0,
            font=font16,
        )  # CURRENT CONDITIONS
        draw.text((0, 50), "Temp", fill=0, font=font12)  # CURRENT TEMP LABEL
        draw.text(
            (0, 60),
            str(round(current_info["temp"]))+ str("\xb0"),
            fill=0,
            font=font20,
        )  # CURRENT TEMP
        draw.text((10, 84), "Feels LIke", fill=0, font=font12)  # CURRENT FEELS LIKE LABEL
        draw.text(
            (10, 93),
            str(round(current_info["feels_like"]))+ str("\xb0"),
            fill=0,
            font=font20,
        )  # CURRENT FEELS LIKE
        draw.text(
            (90, 45),
            self.weather.current_daymax()+ str("\xb0"),
            fill=0,
            font=font20,
        )  # CURRENT DAY HIGH
        draw.text(
            (90, 68),
            self.weather.current_daymin()+ str("\xb0"),
            fill=0,
            font=font20,
        )  # CURRENT DAY LOW
        draw.text((2, 115), "Wind", fill=0, font=font12)
        draw.text(
            (2, 130),
            str(current_info["wind_speed"])
            + " "
            + str(self.weather.wind_dir(current_info["wind_deg"])),
            fill=0,
            font=font14,
        )  # CURRENT WIND
        draw.text((165, 121), "Rain 24h", fill=0, font=font12)
        if "rain" in day_info:
            day_rain = day_info["rain"]
        else:
            day_rain = 0
        draw.text(
            (165, 135),
            str(round(day_info["pop"] * 100)) + "%/" + str(round(day_rain)) + " mm",
            fill=0,
            font=font12,
        )  # Day Rain
        self.epd.display(self.epd.getbuffer(Himage))
        self.epd_finish()

        return draw

    def draw7in5(self, epd):  # 800 x 480
        HimageBlack = Image.new(
            "1", (epd.width, epd.height), 255
        )  # 255: clear the frame
        HimageRed = Image.new("1", (epd.width, epd.height), 255)  # 255: clear the frame
        
        current_info = self.weather.get_current()
        day_info = self.weather.get_daily(0)
        hour_info = self.weather.get_hourly(0)
        epaperBlack7x5img = ImageDraw.Draw(HimageBlack)
        epaperRed7x5img = ImageDraw.Draw(HimageRed)

        epaperBlack7x5img.rectangle(
            (5, 5, 795, 475), fill=255, outline=0, width=2
        )  # INNER FRAME
        epaperBlack7x5img.line(
            (400, 5, 400, 220), fill=0, width=1
        )  # VERTICAL SEPARATION
        epaperBlack7x5img.line(
            (5, 220, 795, 220), fill=0, width=1
        )  # HORIZONTAL SEPARATION
        epaperBlack7x5img.line(
            (5, 350, 795, 350), fill=0, width=1
        )  # HORIZONTAL SEPARATION
        epaperRed7x5img.text(
            (410, 10), self.weather.current_time(), fill=0, font=font24
        )  # TIME
        icon_list = []
        for i in current_info["weather"]:
            icon = self.weather.get_icon(i["icon"])
            icon_list.append(icon)
            cur_condition = self.weather.weather_description(
                self.weather.current_weather()
            )[1]
        if len(icon_list) == 2:
            cur_icon_name1 = icon_list[0]
            cur_icon_name2 = icon_list[1]
            cur_icon1 = Image.open(cur_icon_name1)  # .convert('LA')
            cur_icon2 = Image.open(cur_icon_name2)  # .convert('LA')
            cur_icon1 = cur_icon1.resize((30, 30), None, None, 3)
            cur_icon2 = cur_icon2.resize((30, 30), None, None, 3)
            HimageRed.paste(cur_icon1, (120, 90))
            HimageRed.paste(cur_icon2, (120, 120))
        elif len(icon_list) == 1:
            cur_icon_name1 = icon_list[0]
            cur_icon1 = Image.open(cur_icon_name1)  # .convert('LA')
            cur_icon1 = cur_icon1.resize((80, 80), None, None, 3)
            HimageRed.paste(cur_icon1, (150, 80))
        epaperBlack7x5img.text(
            (10, 10), cur_condition.upper(), fill=0, font=font24
        )  # CURRENT Condition
        epaperRed7x5img.text(
            (10, 35),
            str(round(current_info["temp"]))
            + "\N{DEGREE SIGN}/"
            + str(round(current_info["feels_like"]))
            + "\N{DEGREE SIGN}",
            fill=0,
            font=font48,
        )  # CURRENT TEMP
        epaperBlack7x5img.text((10, 90), "Clouds", fill=0, font=font16)
        epaperBlack7x5img.text(
            (10, 106), str(current_info["clouds"]) + "%", fill=0, font=font24
        )  # CLOUD COVER
        epaperBlack7x5img.text((250, 10), "High/Low", fill=0, font=font24)
        epaperBlack7x5img.text(
            (250, 34),
            self.weather.current_daymax()
            + "\N{DEGREE SIGN}/"
            + self.weather.current_daymin()
            + "\N{DEGREE SIGN}",
            fill=0,
            font=font36,
        )  # CURRENT HIGH/LOW
        epaperBlack7x5img.text((300, 165), "Wind", fill=0, font=font16)
        epaperBlack7x5img.text(
            (300, 180),
            str(current_info["wind_speed"])
            + " "
            + str(self.weather.wind_dir(current_info["wind_deg"])),
            fill=0,
            font=font24,
        )  # CURRENT WIND
        epaperBlack7x5img.text((10, 150), "Rain %/mm", fill=0, font=font16)
        epaperBlack7x5img.text((10, 165), "Hour and Day", fill=0, font=font16)
        if "rain" in hour_info:
            hour_rain = hour_info["rain"]["1h"]
        else:
            hour_rain = 0
        if "rain" in day_info:
            day_rain = day_info["rain"]
        else:
            day_rain = 0
        epaperBlack7x5img.text(
            (10, 180),
            str(round(hour_info["pop"] * 100))
            + "%/"
            + str(round(hour_rain))
            + " "
            + str(round(day_info["pop"] * 100))
            + "%/"
            + str(round(day_rain)),
            fill=0,
            font=font24,
        )  # Hour/Day Rain
        epaperBlack7x5img.text((200, 165), "Humidity", fill=0, font=font16)
        epaperBlack7x5img.text(
            (200, 180), str(current_info["humidity"]) + "%", fill=0, font=font24
        )  # HUMIDTY

        epaperBlack7x5img.text(
            (290, 90), self.weather.current_sunrise(), fill=0, font=font24
        )  # SUNRISE TIME
        epaperBlack7x5img.text(
            (290, 120), self.weather.current_sunset(), fill=0, font=font24
        )  # SUNSET TIME
        sunrise_icon = Image.open(app_dir + "/static_icons/sunrise.bmp")
        sunrise_icon = sunrise_icon.resize((30, 30))
        sunset_icon = Image.open(app_dir + "/static_icons/sunset.bmp")
        sunset_icon = sunset_icon.resize((30, 30))
        HimageRed.paste(sunrise_icon, (250, 90))
        HimageRed.paste(sunset_icon, (250, 120))

        news_selected = self.news.selected_title(self.news_updates)
        epaperBlack7x5img.text((410, 40), "News: ", fill=0, font=font24)
        epaperBlack7x5img.text((420, 70), news_selected[0][0], fill=0, font=font16)
        epaperBlack7x5img.text((420, 90), news_selected[1][0], fill=0, font=font16)
        epaperBlack7x5img.text((420, 110), news_selected[2][0], fill=0, font=font16)
        epaperBlack7x5img.text((420, 130), news_selected[3][0], fill=0, font=font16)

        time = "hour"
        # day_pixel_array = [[15,350],[115,350],[215,350],[315,350],[415,350],[515,350],[615,350],[715,350]]
        hour_pixel_array = [
            [15, 220],
            [130, 220],
            [245, 220],
            [360, 220],
            [475, 220],
            [590, 220],
            [705, 220],
        ]
        hour_span = 3
        i = 0
        for start_pixel in hour_pixel_array:
            hour_info = self.forecast(time, i)
            epaperBlack7x5img, icon = self.hour_summary_large(
                epaperBlack7x5img, hour_info, start_pixel
            )
            HimageRed.paste(icon, (start_pixel[0] + 15, start_pixel[1] + 20))
            i = i + hour_span

        time = "day"
        day_pixel_array = [
            [15, 350],
            [130, 350],
            [245, 350],
            [360, 350],
            [475, 350],
            [590, 350],
            [705, 350],
        ]
        start_pixel = [0, 20]
        i = 0
        for start_pixel in day_pixel_array:
            day_info = self.forecast(time, i)
            epaperBlack7x5img, icon = self.day_summary_large(
                epaperBlack7x5img, day_info, start_pixel
            )
            HimageRed.paste(icon, (start_pixel[0] + 15, start_pixel[1] + 20))
            i = i + 1

        epd.display(epd.getbuffer(HimageBlack), epd.getbuffer(HimageRed))
        self.epd_finish()

        return epaperBlack7x5img, epaperRed7x5img

        ###################################################################################################################
        # PRESSURE & TEMPERATURE
        pression = []
        temperature = []
        maxi = 440  # MAX VERT. PIXEL OF THE GRAPH
        mini = 360  # MIN VERT PIXEL OF THE GRAPH
        x = [55, 105, 155, 205, 255, 305, 355]  # X value of the points
        j = ["J-6", "J-5", "J-4", "J-3", "J-2", "J-1", "J"]  # LABELS

        self.weather.graph_p_t()
        data = self.weather.prevision[1]
        global been_reboot
        if been_reboot == 1:
            try:
                file = open("saved.txt", "r")
                self.weather.prevision[1] = json.loads(file.read())
                data = self.weather.prevision[1]
                been_reboot = 0
                file.close()
            except:
                pass

        else:
            pass

        file = open("saved.txt", "w")
        file.write(str(data))
        file.close()
        for i in range(len(data)):
            pression.append(data[i][0])
            temperature.append(data[i][1])

        # PRESSURE
        self.display.draw_black.line(
            (40, mini, 40, maxi + 20), fill=0, width=1
        )  # GRAPH AXIS
        self.display.draw_black.text(
            (10, mini), str(max(pression)), fill=0, font=font12
        )  # MAX AXIS GRAPH LABEL
        self.display.draw_black.text(
            (10, maxi), str(min(pression)), fill=0, font=font12
        )  # MIN AXIS GRAPH LABEL
        self.display.draw_black.text(
            (10, mini + (maxi - mini) // 2),
            str((max(pression) + min(pression)) // 2),
            fill=0,
            font=font12,
        )  # MID VALUE LABEL
        for i in range(len(x)):  # UPDATE CIRCLE POINTS
            self.display.draw_black.text((x[i], 455), j[i], fill=0, font=font12)
            self.display.draw_circle(
                x[i],
                map_resize(pression[i], min(pression), max(pression), maxi, mini),
                3,
                "r",
            )
        for i in range(len(x) - 1):  # UPDATE LINE
            self.display.draw_red.line(
                (
                    x[i],
                    map_resize(pression[i], min(pression), max(pression), maxi, mini),
                    x[i + 1],
                    map_resize(
                        pression[i + 1], min(pression), max(pression), maxi, mini
                    ),
                ),
                fill=0,
                width=2,
            )
        # TEMPERATURE
        self.display.draw_black.line(
            (430, mini, 430, maxi + 20), fill=0, width=1
        )  # GRAPH AXIS
        self.display.draw_black.text(
            (410, mini), str(max(temperature)), fill=0, font=font12
        )  # MAX AXIS GRAPH LABEL
        self.display.draw_black.text(
            (410, maxi), str(min(temperature)), fill=0, font=font12
        )  # MIN AXIS GRAPH LABEL
        self.display.draw_black.text(
            (410, mini + (maxi - mini) // 2),
            str((max(temperature) + min(temperature)) // 2),
            fill=0,
            font=font12,
        )  # MID VALUE LABEL
        for i in range(len(x)):  # UPDATE CIRCLE POINTS
            self.display.draw_black.text((x[i] + 400, 455), j[i], fill=0, font=font12)
            self.display.draw_circle(
                x[i] + 400,
                map_resize(
                    temperature[i], min(temperature), max(temperature), maxi, mini
                ),
                3,
                "r",
            )
        for i in range(len(x) - 1):  # UPDATE LINE
            self.display.draw_red.line(
                (
                    x[i] + 400,
                    map_resize(
                        temperature[i], min(temperature), max(temperature), maxi, mini
                    ),
                    x[i + 1] + 400,
                    map_resize(
                        temperature[i + 1],
                        min(temperature),
                        max(temperature),
                        maxi,
                        mini,
                    ),
                ),
                fill=0,
                width=2,
            )

        ###################################################################################################################


def main():
    weather = Weather(lat, lon, api_key_weather)
    news = News(news_width, api_key_news)
    if debug == True:
        logger.info("Debug is On")
    else:
        logger.info("Debug is Off")
    if screen_size == "2.7in":
        logger.info("Initializing EPD for 2.7in")
        epd = epd2in7.EPD()
        weather_station_inst = weather_station(epd, weather, news)
        logger.info("Creating Buttons")
        btn1 = Button(5)
        btn1.when_pressed = weather_station_inst.button1
        btn2 = Button(6)
        btn2.when_pressed = weather_station_inst.button2
        btn3 = Button(13)
        btn3.when_pressed = weather_station_inst.button3
        btn4 = Button(19)
        btn4.when_pressed = weather_station_inst.button6
        while True:
            logger.info("Updating Screen")
            epd = epd2in7.EPD()
            weather_station_inst = weather_station(epd, weather, news)
            if debug == True:
                sleep_time = 15
            else:
                sleep_time = 225

            weather_station_inst.button1()
            time.sleep(sleep_time)
            weather_station_inst.button2()
            time.sleep(sleep_time)
            weather_station_inst.button3()
            time.sleep(sleep_time)
            weather_station_inst.button6()
            time.sleep(sleep_time)
            weather_station_inst.button5()
            time.sleep(sleep_time)

            logger.info("Screen is drawn")
            logger.info("Going to sleep.")
            logger.info("------------")
            if debug == True:
                sys.exit(0)
    elif screen_size == "7x5in":
        logger.info("Initializing EPD for 7x5in")
        epd = epd7in5b_V2.EPD()
        while True:
            logger.info("Drawing screen")
            weather_station_inst = weather_station(epd, weather, news)
            weather_station_inst.draw7in5(epd)
            logger.info("Screen is drawn")
            logger.info("Going to sleep.")
            logger.info("------------")
            if debug == True:
                sys.exit(0)
            time.sleep(900)


if __name__ == "__main__":
    main()
