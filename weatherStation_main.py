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
        # self.epd.Clear(0xFF)

    def button1(self):  # Home Button
        logger.info("Drawing Button 1 screen")
        self.weather.update()
        self.news.update()
        draw = self.draw2in7(self.epd)
        return 0

    def button2(self):  # Hourly Forecast
        logger.info("Drawing Hourly Forecast")
        Himage = Image.new(
            "1", (self.epd.height, self.epd.width), 255
        )  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw.text((0, 0), self.weather.current_time(), fill=0, font=font16)
        draw.line((0, 20, 264, 20), fill=0, width=1)
        time = "hour"
        hour_pixel_array = [
            [0, 20],
            [66, 20],
            [132, 20],
            [198, 20],
            [0, 100],
            [66, 100],
            [132, 100],
            [198, 100],
        ]
        hour_span = 3
        i = 0
        for start_pixel in hour_pixel_array:
            hour_info = self.forecast(time, i)
            draw, icon = self.hour_summary(draw, hour_info, start_pixel)
            Himage.paste(icon, (start_pixel[0], start_pixel[1] + 13))
            i = i + hour_span
        self.epd.display(self.epd.getbuffer(Himage))
        return 0

    def button3(self):  # Daily Forecast
        logger.info("Drawing Daily Forecast")
        Himage = Image.new(
            "1", (self.epd.height, self.epd.width), 255
        )  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw.text((0, 0), self.weather.current_time(), fill=0, font=font16)
        draw.line((0, 20, 264, 20), fill=0, width=1)
        start_pixel = [0, 20]
        time = "day"
        day_pixel_array = [
            [0, 20],
            [66, 20],
            [132, 20],
            [198, 20],
            [0, 100],
            [66, 100],
            [132, 100],
            [198, 100],
        ]
        i = 0
        for start_pixel in day_pixel_array:
            day_info = self.forecast(time, i)
            draw, icon = self.day_summary(draw, day_info, start_pixel)
            Himage.paste(icon, (start_pixel[0], start_pixel[1] + 13))
            i = i + 1
        self.epd.display(self.epd.getbuffer(Himage))
        return 0

    def button4(self):
        logger.info("Drawing Button 4 screen")
        Himage = Image.new(
            "1", (self.epd.height, self.epd.width), 255
        )  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw = self.open_framework(draw)
        news_updates = self.news.update()
        news_selected = self.news.selected_title(news_updates)
        draw.text((0, 155), "News: ", fill=0, font=font12)
        draw.text((35, 155), news_selected[0][0], fill=0, font=font12)
        draw.line((88, 20, 88, 150), fill=0, width=1)  # VERTICAL SEPARATION
        draw.line((176, 20, 176, 150), fill=0, width=1)  # VERTICAL SEPARATION
        start_pixel = [0, 20]
        time = "day"
        day_pixel_array = [[0, 20], [89, 20], [177, 20]]
        i = 0
        for start_pixel in day_pixel_array:
            day_info = self.forecast(time, i)
            draw, icon = self.day_summary(draw, day_info, start_pixel)
            Himage.paste(icon, (start_pixel[0], start_pixel[1] + 13))
            i = i + 1
        self.epd.display(self.epd.getbuffer(Himage))
        return 0

    def button5(self):  # Other Stuff
        logger.info("Drawing Button 5 screen")
        Himage = Image.new(
            "1", (self.epd.height, self.epd.width), 255
        )  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw = self.framework(draw)
        hour_temps = []
        hour_feels = []
        for i in self.weather.get_hourly(None, 8):
            hour_temps.append(i["temp"])
            hour_feels.append(i["feels_like"])
        draw.text((165, 20), "CO", fill=0, font=font12)
        draw.text((165, 30), str(self.weather.co()), fill=0, font=font20)
        draw.text((165, 50), "NO", fill=0, font=font12)
        draw.text((165, 60), str(self.weather.no()), fill=0, font=font20)
        draw.text((165, 80), "NO2", fill=0, font=font12)
        draw.text((165, 90), str(self.weather.no2()), fill=0, font=font20)
        draw.text((165, 110), "Ozone", fill=0, font=font12)
        draw.text((165, 120), str(self.weather.o3()), fill=0, font=font20)
        draw = self.data_graph(
            self.weather, draw, hour_temps, ["temp/feels like"], [55, 140], [5, 75]
        )
        draw = self.data_graph(
            self.weather, draw, hour_feels, [""], [55, 140], [5, 75]
        )
        self.epd.display(self.epd.getbuffer(Himage))
        return 0

    def three_day_forecast(self):  # Weekend Forecast
        day_pixel_array = [
            [0, 20],
            [66, 20],
            [132, 20],
        ]
        time = "day"
        i = 1
        for start_pixel in day_pixel_array:
            day_info = self.forecast(time, i)
            #draw.line((88, 20, 88, 150), fill=0, width=1)  # VERTICAL SEPARATION
            draw, icon = self.day_summary(draw, day_info, start_pixel)
            Himage = Image.new(
                "1", (self.epd.height, self.epd.width), 255
            )  # 255: clear the frame
            Himage.paste(icon, (start_pixel[0], start_pixel[1] + 13))
            i = i + 1
        self.epd.display(self.epd.getbuffer(Himage))
        return 0

    def data_graph(
        self,
        weather,
        draw,
        weather_data,
        elements,
        graph_dim,
        start_pixel,
        fill_col="black",
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
        for i in elements:
            last_start_h = 0
            last_start_v = 0
            for j in weather_data:
                start_h = corner[0] - dot_size + (pixel_spacing * (iter + 1))
                start_v = corner[1] - dot_size - weather_data[iter]
                finish_h = corner[0] + dot_size + (pixel_spacing * (iter + 1))
                finish_v = corner[1] + dot_size - weather_data[iter]
                draw.ellipse(
                    (round(start_h), round(start_v), round(finish_h), round(finish_v)),
                    fill=fill_col,
                )
                if last_start_h != 0:
                    draw.line((last_start_h + (dot_size / 2) , last_start_v - (dot_size / 2), finish_h, finish_v),fill=0,width=1)
                last_start_h = start_h
                last_start_v = start_v
                iter = iter + 1
            draw.text(
                (corner[0] + (graph_dim[1] / 2), corner[1]),
                i.upper(),
                fill=0,
                font=font8,
            )
        return draw

    def open_framework(self, draw):
        draw.text((0, 0), self.weather.current_time(), fill=0, font=font16)
        draw.line((0, 20, 264, 20), fill=0, width=1)  # HORIZONTAL SEPARATION
        draw.line((0, 150, 264, 150), fill=0, width=1)  # HORIZONTAL SEPARATION
        return draw

    def framework(self, draw):
        draw.text((0, 0), self.weather.current_time(), fill=0, font=font16)
        draw.line((0, 20, 264, 20), fill=0, width=1)  # HORIZONTAL SEPARATION
        draw.line((0, 150, 264, 150), fill=0, width=1)  # HORIZONTAL SEPARATION
        draw.line((162, 20, 162, 150), fill=0, width=1)  # VERTICAL SEPARATION
        news_updates = self.news.update()
        news_selected = self.news.selected_title(news_updates)
        draw.text((0, 155), "News: ", fill=0, font=font12)
        draw.text((38, 155), news_selected[0][0], fill=0, font=font12)
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
            str(day_info[2]),
            fill=0,
            font=font16,
        )  # DAY HIGH
        draw.text(
            (start_pixel[0] + 35, start_pixel[1] + 35),
            str(day_info[3]),
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
            (start_pixel[0] + 35, start_pixel[1] + 12),
            str(hour_info[2]),
            fill=0,
            font=font16,
        )  # HOUR TEMP
        draw.text(
            (start_pixel[0] + 35, start_pixel[1] + 35),
            str(hour_info[3]),
            fill=0,
            font=font16,
        )  # HOUR FEELS LIKE
        draw.text(
            (start_pixel[0] + 40, start_pixel[1] + 27), "degs", fill=0, font=font8
        )  # HOUR TEMP
        draw.text(
            (start_pixel[0] + 40, start_pixel[1] + 50), "feels", fill=0, font=font8
        )  # HOUR FEELS LIKE
        draw.text(
            (start_pixel[0], start_pixel[1] + 53),
            str(hour_info[5]) + "% " + str(hour_info[6]),
            fill=0,
            font=font12,
        )
        draw.text(
            (start_pixel[0], start_pixel[1] + 63),
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

    def draw2in7(self, epd):
        Himage = Image.new(
            "1", (self.epd.height, self.epd.width), 255
        )  # 255: clear the frame
        self.weather.update()
        self.weather.update_pol()
        self.news.update()
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
        test_image = ImageDraw.Draw(Himage)
        test_image = self.framework(test_image)
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
        test_image.text((165, 20), "Sunrise", fill=0, font=font12)
        test_image.text(
            (165, 30), self.weather.current_sunrise(), fill=0, font=font20
        )  # SUNRISE TIME
        test_image.text((165, 50), "Sunset", fill=0, font=font12)
        test_image.text(
            (165, 60), self.weather.current_sunset(), fill=0, font=font20
        )  # SUNSET TIME
        test_image.text((165, 80), "Humidity %", fill=0, font=font12)
        test_image.text(
            (165, 90), str(current_info["humidity"]), fill=0, font=font20
        )  # HUMIDTY
        test_image.text((165, 110), "Cloud %", fill=0, font=font12)
        test_image.text(
            (165, 120), str(current_info["clouds"]), fill=0, font=font16
        )  # CLOUD COVER
        test_image.text((220, 110), "UVI", fill=0, font=font12)
        test_image.text(
            (220, 120), str(current_info["uvi"]), fill=0, font=font16
        )  # UVI
        test_image.text(
            (0, 20), "Current conditions", fill=0, font=font12
        )  # CURRENT CONDITIONS LABEL
        test_image.text(
            (0, 30),
            self.weather.weather_description(self.weather.current_weather())[1],
            fill=0,
            font=font16,
        )  # CURRENT CONDITIONS
        test_image.text(
            (0, 48), "Temp/Feels Like", fill=0, font=font12
        )  # CURRENT TEMP LABEL
        test_image.text(
            (0, 56),
            str(round(current_info["temp"])) + "/" + str(round(current_info["feels_like"])),
            fill=0,
            font=font24,
        )  # CURRENT TEMP and FEELS LIKE
        test_image.text((85, 63), "High/Low", fill=0, font=font12)
        test_image.text(
            (80, 70),
            self.weather.current_daymax() + "/" + self.weather.current_daymin(),
            fill=0,
            font=font24,
        )  # CURRENT DAY HIGH/LOW
        test_image.text((0, 90), "Current Wind", fill=0, font=font12)
        test_image.text(
            (0, 102),
            str(current_info["wind_speed"])
            + " "
            + str(self.weather.wind_dir(current_info["wind_deg"])),
            fill=0,
            font=font14,
        )  # CURRENT WIND
        test_image.text((0, 116), "Rain 24h", fill=0, font=font12)
        if "rain" in day_info:
            day_rain = day_info["rain"]
        else:
            day_rain = 0
        test_image.text(
            (0, 130),
            str(round(day_info["pop"] * 100)) + "%/" + str(round(day_rain)) + " mm",
            fill=0,
            font=font12,
        )  # Day Rain
        epd.display(epd.getbuffer(Himage))

        return test_image

    def draw7in5(self, epd):  # 800 x 480
        HimageBlack = Image.new(
            "1", (epd.width, epd.height), 255
        )  # 255: clear the frame
        HimageRed = Image.new("1", (epd.width, epd.height), 255)  # 255: clear the frame
        self.weather.update()
        self.weather.update_pol()
        self.news.update()
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

        news_updates = self.news.update()
        news_selected = self.news.selected_title(news_updates)
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
        btn4.when_pressed = weather_station_inst.button5
        while True:
            weather_station_inst = weather_station(epd, weather, news)
            if debug == True:
                sleep_time = 15
            else:
                sleep_time = 225
            '''
            weather_station_inst.button1()
            time.sleep(sleep_time)
            weather_station_inst.button2()
            time.sleep(sleep_time)
            weather_station_inst.button3()
            time.sleep(sleep_time)
            weather_station_inst.button4()            
            time.sleep(sleep_time)
            '''
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
