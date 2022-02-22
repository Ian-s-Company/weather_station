

from weather import *
from news import *
from display import *
import json
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from gpiozero import Button # Pins 5,6,13,19
import logging

screen_size = ""

try:
    screen_size = sys.argv[1]
    # like 7x5in
except:
    screen_size = "2.7in" #176x264

try:
     lat = sys.argv[1]
except:
     lat = "33.104191"

try:
     lon = sys.argv[2]
except:
     lon = "-96.671738"

try:
     api_key_weather = sys.argv[3]
except:
     api_key_weather = "696a01e644791c546061076bc92e4cb4"

try:
     api_key_news = sys.argv[4]
except:
     api_key_news = "3ac6eaa80651499ea0c931a93104b260"

been_reboot = 1
home_dir = "/home/pi/WEATHER_STATION_PI/"
debug = 0
logging.basicConfig(filename=home_dir + 'weatherStation.log', filemode='w', level=logging.DEBUG)

if debug == 0 and screen_size == "7x5in":
    logging.info("Screen size is 7x5 ")
    import epd7in5b_V2 
elif debug == 0 and screen_size == "2.7in":
    logging.info("Screen size is 2in7")
    news_width = 170
    import epd2in7
else:
    pass

def map_resize(val, in_mini, in_maxi, out_mini, out_maxi):
    if in_maxi - in_mini != 0:
        out_temp = (val - in_mini) * (out_maxi - out_mini) // (in_maxi - in_mini) + out_mini
    else:
        out_temp = out_mini
    return out_temp

class weather_station:

    def __init__(self,epd,weather,news):
        self.epd = epd
        self.weather = weather
        self.news = news
        self.epd.init()
        #self.epd.Clear(0xFF)

    def button1(self): #Home Button
        logging.info("Drawing Button 1 screen")
        self.weather.update()
        self.news.update(api_key_news)
        draw = self.draw2in7(self.epd)
        return 0

    def button2(self): # Hourly Forecast
        logging.info("Drawing Hourly Forecast")
        Himage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw.text((0, 0), self.weather.current_time(), fill=0, font=font16)  
        draw.line((0, 20, 264, 20), fill=0, width=1) 
        time = 'hour'
        hour_pixel_array = [[0,20],[66,20],[132,20],[198,20],[0,100],[66,100],[132,100],[198,100]]
        hour_span = 3
        i = 0
        for start_pixel in hour_pixel_array:
            hour_info = self.forecast(time, i)
            draw,icon = self.hour_summary(draw, hour_info, start_pixel)
            Himage.paste(icon,(start_pixel[0],start_pixel[1] + 13))
            i = i + hour_span
        self.epd.display(self.epd.getbuffer(Himage))
        return 0

    def button3(self): # Daily Forecast
        logging.info("Drawing Daily Forecast")
        Himage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw.text((0, 0), self.weather.current_time(), fill=0, font=font16)  
        draw.line((0, 20, 264, 20), fill=0, width=1) 
        start_pixel = [0,20]
        time = 'day'
        day_pixel_array = [[0,20],[66,20],[132,20],[198,20],[0,100],[66,100],[132,100],[198,100]]
        i = 0
        for start_pixel in day_pixel_array:
            day_info = self.forecast(time, i)
            draw,icon = self.day_summary(draw, day_info, start_pixel)
            Himage.paste(icon,(start_pixel[0],start_pixel[1] + 13))
            i = i + 1
        self.epd.display(self.epd.getbuffer(Himage))
        return 0

    def button5(self): #Other Stuff

        logging.info("Drawing Button 4 screen")
        Himage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw = self.framework(draw)
        hour_temps = []
        hour_feels = []
        for i in self.weather.get_hourly(None,8):
            hour_temps.append(i['temp'])
            hour_feels.append(i['feels_like'])
        #print(hour_temps)
        draw.text((165, 20), "CO", fill=0, font=font12)  
        draw.text((165, 30), str(self.weather.co()), fill=0, font=font24)
        draw.text((165, 50), "NO", fill=0, font=font12)  
        draw.text((165, 60), str(self.weather.no()), fill=0, font=font24)
        draw.text((165, 80), "NO2", fill=0, font=font12)  
        draw.text((165, 90), str(self.weather.no2()), fill=0, font=font24)
        draw.text((165, 110), "Ozone", fill=0, font=font12)  
        draw.text((165, 120), str(self.weather.o3()), fill=0, font=font24) 
        draw = self.data_graph(self.weather, draw, hour_temps, ['temp'], [55,140], [5, 25], 'black')
        draw = self.data_graph(self.weather, draw, hour_feels, ['feels_like'], [55,140], [5, 83], 'black')
        self.epd.display(self.epd.getbuffer(Himage))
        return 0

    def button4(self):

        logging.info("Drawing Button 5 screen")
        Himage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw = self.open_framework(draw)
        news_selected = self.news.selected_title()
        draw.text((0, 155), "News:", fill=0, font=font12) 
        draw.text((30, 155), news_selected[0][0], fill=0, font=font12) 
        draw.line((88, 20, 88, 150), fill=0, width=1)  # VERTICAL SEPARATION
        draw.line((176, 20, 176, 150), fill=0, width=1)  # VERTICAL SEPARATION
        start_pixel = [0,20]
        time = 'day'
        day_pixel_array = [[0,20],[89,20],[177,20]]
        i = 0
        for start_pixel in day_pixel_array:
            day_info = self.forecast(time, i)
            draw,icon = self.day_summary(draw, day_info, start_pixel)
            Himage.paste(icon,(start_pixel[0],start_pixel[1] + 13))
            i = i + 1
        self.epd.display(self.epd.getbuffer(Himage))

    def three_day_forecast(self, weather, draw): # Weekend Forecast
        for start_pixel in day_pixel_array:
            day_info = self.forecast(time, i)
            draw,icon = self.day_summary(self.weather, draw, day_info, start_pixel)
            Himage.paste(icon,(start_pixel[0],start_pixel[1] + 13))
            i = i + 1
        self.epd.display(self.epd.getbuffer(Himage))
        return 0

    def data_graph(self, weather, draw, weather_data, elements, graph_dim, start_pixel, fill_col='black'): # weather data is array of data, elements is the data field to be graphed
        corner = [start_pixel[0], start_pixel[1] + graph_dim[0]]
        draw.line((start_pixel[0], start_pixel[1] + graph_dim[0], start_pixel[0] + graph_dim[1], start_pixel[1] + graph_dim[0] ), fill=0, width=1)  # HORIZONTAL LINE
        draw.line((start_pixel[0], start_pixel[1], start_pixel[0], start_pixel[1] + graph_dim[0] ), fill=0, width=1)  # VERTICAL LINE
        pixel_spacing = int(graph_dim[1] / len(weather_data))
        dot_size = 2
        iter = 0 
        for i in elements:
            for j in weather_data:
                #print("Pixel Spacing is: " + str(pixel_spacing) + ",Element: " + str(i) + ", Weather Data: " + str(j))
                start_h = corner[0] - dot_size + (pixel_spacing * (iter + 1))
                start_v = corner[1] - dot_size - weather_data[iter]
                finish_h = corner[0] + dot_size + (pixel_spacing * (iter + 1))
                finish_v = corner[1] + dot_size - weather_data[iter]
                #print("Start H " + str(start_h) + ",Start V " + str(start_v) + ",Finish H " + str(finish_h) + ",Finish V " + str(finish_v))
                draw.ellipse((round(start_h), round(start_v), round(finish_h), round(finish_v)), fill = fill_col)
                iter = iter + 1
            draw.text((corner[0] + (graph_dim[1] / 2), corner[1]), i.upper() , fill=0, font=font12)  
        return draw
    
    def open_framework(self, draw):
        draw.text((0, 0), self.weather.current_time(), fill=0, font=font16)  # SUNRISE TIME
        draw.line((0, 20, 264, 20), fill=0, width=1)  # HORIZONTAL SEPARATION
        draw.line((0, 150, 264, 150), fill=0, width=1)  # HORIZONTAL SEPARATION
        return draw

    def framework(self, draw):
        draw.text((0, 0), self.weather.current_time(), fill=0, font=font16)  # SUNRISE TIME
        draw.line((0, 20, 264, 20), fill=0, width=1)  # HORIZONTAL SEPARATION
        draw.line((0, 150, 264, 150), fill=0, width=1)  # HORIZONTAL SEPARATION
        draw.line((162, 20, 162, 150), fill=0, width=1)  # VERTICAL SEPARATION
        news_selected = self.news.selected_title()
        draw.text((0, 155), "News:", fill=0, font=font12) 
        draw.text((30, 155), news_selected[0][0], fill=0, font=font12) 
        return draw

    def forecast(self, day_or_hour, no_of_time):
        if day_or_hour == 'day':
            weather_info = self.weather.get_daily(no_of_time)
            name = datetime.fromtimestamp(weather_info['dt']).strftime('%A')
            high = round(weather_info['temp']['max'])
            low = round(weather_info['temp']['min'])
        elif day_or_hour == 'hour':
            weather_info = self.weather.get_hourly(no_of_time)
            name = datetime.fromtimestamp(weather_info['dt']).strftime('%H:%M')
            high = round(weather_info['temp'])
            low = round(weather_info['feels_like'])
        icon_list = []
        for i in weather_info['weather']:
            icon = self.weather.get_icon(i['icon'])
            icon_list.append(icon)
        icon = icon_list[0]
        detail = weather_info['weather'][0]['description']
        pop = str(round(weather_info['pop'] * 100))
        if 'rain' in weather_info:
            if day_or_hour == 'hour':
                rain = weather_info['rain']['1h']
            elif day_or_hour == 'day':
                rain = weather_info['rain']
            rain = round(rain)
            rain = str(rain)
        else:
            rain = 0
        w_spd = round(weather_info['wind_speed'])
        w_dir = round(weather_info['wind_deg'])
        return icon, detail, high, low, name, pop, rain, w_spd, w_dir

    def day_summary(self, draw, day_info, start_pixel):
        draw.text((start_pixel[0],start_pixel[1]), day_info[4], fill=0, font=font12) # DAY NAME
        draw.text((start_pixel[0] + 35, start_pixel[1] + 12), str(day_info[2]), fill=0, font=font16) #DAY HIGH
        draw.text((start_pixel[0] + 35, start_pixel[1] + 35), str(day_info[3]), fill=0, font=font16) #DAY LOW
        draw.text((start_pixel[0], start_pixel[1] + 53), str(day_info[5]) + "% " + str(day_info[6]), fill=0, font=font12)
        draw.text((start_pixel[0], start_pixel[1] + 63), str(day_info[7]) + "mph " + self.weather.wind_dir(day_info[8]), fill=0, font=font12)
        icon = Image.open(day_info[0])
        icon = icon.resize((30,30))
        return draw, icon

    def hour_summary(self, draw, hour_info, start_pixel):
        draw.text((start_pixel[0],start_pixel[1]), hour_info[4], fill=0, font=font12) # HOUR
        draw.text((start_pixel[0] + 35, start_pixel[1] + 12), str(hour_info[2]), fill=0, font=font16) #HOUR TEMP
        draw.text((start_pixel[0] + 35, start_pixel[1] + 35), str(hour_info[3]), fill=0, font=font16) #HOUR FEELS LIKE
        draw.text((start_pixel[0] + 40, start_pixel[1] + 27), "degs", fill=0, font=font8) #HOUR TEMP
        draw.text((start_pixel[0] + 40, start_pixel[1] + 50), "feels", fill=0, font=font8) #HOUR FEELS LIKE
        draw.text((start_pixel[0], start_pixel[1] + 53), str(hour_info[5]) + "% " + str(hour_info[6]), fill=0, font=font12)
        draw.text((start_pixel[0], start_pixel[1] + 63), str(hour_info[7]) + "mph " + self.weather.wind_dir(hour_info[8]), fill=0, font=font12)
        icon = Image.open(hour_info[0])
        icon = icon.resize((30,30))
        return draw, icon

    def draw2in7(self, epd):
        Himage = Image.new('1', (self.epd.height, self.epd.width), 255)  # 255: clear the frame
        self.weather.update()
        self.weather.update_pol()
        self.news.update(api_key_news)
        current_info = self.weather.get_current()
        logging.info("Begin update @" + self.weather.current_time() + " at latitude " + lat + " longitude " + lon)
        day_info = self.weather.get_daily(0)
        hour_info = self.weather.get_hourly(0)
        logging.info(current_info)
        sunrise_icon = Image.open(home_dir + 'static_icons/sunrise.bmp')
        sunrise_icon = sunrise_icon.resize((30,30))
        sunset_icon = Image.open(home_dir + 'static_icons/sunset.bmp')
        sunset_icon = sunset_icon.resize((30,30))
        Himage.paste(sunrise_icon, (225,20))
        Himage.paste(sunset_icon, (225,60))
        test_image = ImageDraw.Draw(Himage)
        test_image = self.framework(test_image)
        icon_list = []
        for i in current_info['weather']:
            icon = self.weather.get_icon(i['icon'])
            icon_list.append(icon)
        cur_condition = self.weather.weather_description(self.weather.current_weather())[1]
        if len(icon_list) == 2:
            cur_icon_name1 = icon_list[0]
            cur_icon_name2 = icon_list[1]
            cur_icon1 = Image.open(cur_icon_name1) #.convert('LA')
            cur_icon2 = Image.open(cur_icon_name2) #.convert('LA')
            cur_icon1 = cur_icon1.resize((30,30),None,None,3)
            cur_icon2 = cur_icon2.resize((30,30),None,None,3)
            Himage.paste(cur_icon1, (120,90))
            Himage.paste(cur_icon2, (120,120))
        elif len(icon_list) == 1: 
            cur_icon_name1 = icon_list[0]
            cur_icon1 = Image.open(cur_icon_name1) #.convert('LA')
            cur_icon1 = cur_icon1.resize((40,40),None,None,3)
            Himage.paste(cur_icon1, (100,100))
        test_image.text((165, 20), "Sunrise", fill=0, font=font12)  
        test_image.text((165, 30), self.weather.current_sunrise(), fill=0, font=font24)  # SUNRISE TIME
        test_image.text((165, 50), "Sunset", fill=0, font=font12)  
        test_image.text((165, 60), self.weather.current_sunset(), fill=0, font=font24)  # SUNSET TIME
        test_image.text((165, 80), "Humidity", fill=0, font=font12)  
        test_image.text((165, 90), str(current_info['humidity']), fill=0, font=font24)  # HUMIDTY
        test_image.text((165, 110), "Clouds", fill=0, font=font12)  
        test_image.text((165, 120), str(current_info['clouds']), fill=0, font=font16)  # CLOUD COVER
        test_image.text((220, 110), "UVI", fill=0, font=font12)  
        test_image.text((220, 120), str(current_info['uvi']), fill=0, font=font16)  # UVI
        test_image.text((0, 20), "Current conditions", fill=0, font=font12)  # CURRENT TEMP
        test_image.text((0, 30), self.weather.weather_description(self.weather.current_weather())[1], fill=0, font=font16)  # CURRENT TEMP
        test_image.text((0, 48), "Current Temp/Feels Like", fill=0, font=font12)  # CURRENT TEMP
        test_image.text((0, 55), str(round(current_info['temp'])), fill=0, font=font36)  # CURRENT FEELS LIKE
        test_image.text((35, 67), "/" + str(round(current_info['feels_like'])), fill=0, font=font24)  # CURRENT TEMP
        test_image.text((80, 60), "High/Low", fill=0, font=font12)  
        test_image.text((80, 70), self.weather.current_daymax() + "/" + self.weather.current_daymin(), fill=0, font=font24)  # CURRENT HIGH/LOW
        test_image.text((0, 90), "Current Wind", fill=0, font=font12)  
        test_image.text((0, 102), str(current_info['wind_speed']) + " " + str(self.weather.wind_dir(current_info['wind_deg'])), fill=0, font=font16)  # CURRENT WIND
        test_image.text((0, 116), "Rain H%/mm D%/mm", fill=0, font=font12)  
        if 'rain' in hour_info:
            hour_rain = hour_info['rain']['1h']
        else:
            hour_rain = 0
        if 'rain' in day_info:
            day_rain = day_info['rain']
        else:
            day_rain = 0
        test_image.text((0, 130), str(round(hour_info['pop'] * 100)) + "%/" + str(round(hour_rain)) + " " + str(round(day_info['pop'] * 100)) + "%/" + str(round(day_rain)), fill=0, font=font16)  # Hour/Day Rain
        epd.display(epd.getbuffer(Himage))

        return test_image

def draw7in5(epd,weather,news,display):

    ##################################################################################################################
    # FRAME
    display.draw_black.rectangle((5, 5, 795, 475), fill=255, outline=0, width=2)  # INNER FRAME
    display.draw_black.line((540, 5, 540, 350), fill=0, width=1)  # VERTICAL SEPARATION
    display.draw_black.line((350, 5, 350, 350), fill=0, width=1)  # VERTICAL SEPARATION slim
    display.draw_black.line((5, 350, 795, 350), fill=0, width=1)  # HORIZONTAL SEPARATION

    # UPDATED AT
    display.draw_black.text((10, 8), "Mis à jour le " + weather.current_time(), fill=0, font=font8)

    ###################################################################################################################
    # CURRENT WEATHER
    display.draw_icon(20, 55, "r", 75, 75,
                      weather.weather_description(weather.current_weather())[0])  # CURRENT WEATHER ICON
    display.draw_black.text((120, 15), weather.current_temp(), fill=0, font=font48)  # CURRENT TEMP
    display.draw_black.text((230, 15), weather.current_hum(), fill=0, font=font48)  # CURRENT HUM
    display.draw_black.text((245, 65), "Humidity", fill=0, font=font12)  # LABEL "HUMIDITY"
    display.draw_black.text((120, 75), weather.wind()[0] + " " + weather.wind()[1], fill=0, font=font24)

    display.draw_icon(120, 105, "b", 35, 35, "sunrise")  # SUNRISE ICON
    display.draw_black.text((160, 110), weather.current_sunrise(), fill=0, font=font16)  # SUNRISE TIME
    display.draw_icon(220, 105, "b", 35, 35, "sunset")  # SUNSET ICON
    display.draw_black.text((260, 110), weather.current_sunset(), fill=0, font=font16)  # SUNSET TIME

    ###################################################################################################################
    # NEXT HOUR RAIN
    try :
        data_rain = weather.rain_next_hour()

        # FRAME
        display.draw_black.text((20, 150), "Pluie dans l'heure - " + time.strftime("%H:%M", time.localtime()), fill=0,
                                font=font16)  # NEXT HOUR RAIN LABEL
        display.draw_black.rectangle((20, 175, 320, 195), fill=255, outline=0, width=1)  # Red rectangle = rain

        # LABEL
        for i in range(len(data_rain)):
            display.draw_black.line((20 + i * 50, 175, 20 + i * 50, 195), fill=0, width=1)
            display.draw_black.text((20 + i * 50, 195), data_rain[i][0], fill=0, font=font16)
            if data_rain[i][1] != 0:
                display.draw_red.rectangle((20 + i * 50, 175, 20 + (i + 1) * 50, 195), fill=0)
    except:
        pass

    ###################################################################################################################
    # HOURLY FORECAST
    display.draw_black.text((30, 227), "+3h", fill=0, font=font16)  # +3h LABEL
    display.draw_black.text((150, 227), "+6h", fill=0, font=font16)  # +6h LABEL
    display.draw_black.text((270, 227), "+12h", fill=0, font=font16)  # +12h LABEL
    # 3H
    display.draw_icon(25, 245, "r", 50, 50,
                      weather.weather_description(weather.hourly_forecast()["+3h"]["id"])[0])  # +3H WEATHER ICON
    display.draw_black.text((25, 295), weather.weather_description(weather.hourly_forecast()["+3h"]["id"])[1], fill=0,
                            font=font12)  # WEATHER DESCRIPTION +3h
    display.draw_black.text((35, 307), weather.hourly_forecast()["+3h"]["temp"], fill=0, font=font16)  # TEMP +3H
    display.draw_black.text((35, 323), weather.hourly_forecast()["+3h"]["pop"], fill=0, font=font16)  # POP +3H
    # +6h
    display.draw_icon(145, 245, "r", 50, 50,
                      weather.weather_description(weather.hourly_forecast()["+6h"]["id"])[0])  # +6H WEATHER ICON
    display.draw_black.text((145, 295), weather.weather_description(weather.hourly_forecast()["+6h"]["id"])[1], fill=0,
                            font=font12)  # WEATHER DESCRIPTION +6h
    display.draw_black.text((155, 307), weather.hourly_forecast()["+6h"]["temp"], fill=0, font=font16)  # TEMP +6H
    display.draw_black.text((155, 323), weather.hourly_forecast()["+6h"]["pop"], fill=0, font=font16)  # POP +6H
    # +12h
    display.draw_icon(265, 245, "r", 50, 50,
                      weather.weather_description(weather.hourly_forecast()["+12h"]["id"])[0])  # +12H WEATHER ICON
    display.draw_black.text((265, 295), weather.weather_description(weather.hourly_forecast()["+12h"]["id"])[1], fill=0,
                            font=font12)  # WEATHER DESCRIPTION +12h
    display.draw_black.text((275, 307), weather.hourly_forecast()["+12h"]["temp"], fill=0, font=font16)  # TEMP +12H
    display.draw_black.text((275, 323), weather.hourly_forecast()["+12h"]["pop"], fill=0, font=font16)  # POP +12H

    ###################################################################################################################
    # DAILY FORECAST
    # +24h
    display.draw_black.text((360, 30), weather.daily_forecast()["+24h"]["date"], fill=0, font=font16)  # +24H DAY
    display.draw_icon(400, 50, "r", 50, 50,
                      weather.weather_description(weather.daily_forecast()["+24h"]["id"])[0])  # +24H WEATHER ICON
    display.draw_black.text((465, 50), weather.daily_forecast()["+24h"]["min"], fill=0, font=font14)
    display.draw_black.text((498, 50), "min", fill=0, font=font14)  # +24H MIN TEMPERATURE
    display.draw_black.text((465, 65), weather.daily_forecast()["+24h"]["max"], fill=0, font=font14)
    display.draw_black.text((498, 65), "max", fill=0, font=font14)  # +24H MAX TEMPERATURE
    display.draw_black.text((465, 80), weather.daily_forecast()["+24h"]["pop"], fill=0, font=font14)
    display.draw_black.text((498, 80), "pluie", fill=0, font=font14)  # +24H RAIN PROBABILITY

    # +48h
    display.draw_black.text((360, 105), weather.daily_forecast()["+48h"]["date"], fill=0, font=font16)  # +48H DAY
    display.draw_icon(400, 125, "r", 50, 50,
                      weather.weather_description(weather.daily_forecast()["+48h"]["id"])[0])  # +48H WEATHER ICON
    display.draw_black.text((465, 125), weather.daily_forecast()["+48h"]["min"], fill=0, font=font14)
    display.draw_black.text((498, 125), "min", fill=0, font=font14)  # +48H MIN TEMPERATURE
    display.draw_black.text((465, 140), weather.daily_forecast()["+48h"]["max"], fill=0, font=font14)
    display.draw_black.text((498, 140), "max", fill=0, font=font14)  # +48H MAX TEMPERATURE
    display.draw_black.text((465, 155), weather.daily_forecast()["+48h"]["pop"], fill=0, font=font14)
    display.draw_black.text((498, 155), "pluie", fill=0, font=font14)  # +48H RAIN PROBABILITY

    # +72h
    display.draw_black.text((360, 180), weather.daily_forecast()["+72h"]["date"], fill=0, font=font16)  # +72H DAY
    display.draw_icon(400, 200, "r", 50, 50,
                      weather.weather_description(weather.daily_forecast()["+72h"]["id"])[0])  # +72H WEATHER ICON
    display.draw_black.text((465, 200), weather.daily_forecast()["+72h"]["min"], fill=0, font=font14)
    display.draw_black.text((498, 200), "min", fill=0, font=font14)  # +72H MIN TEMPERATURE
    display.draw_black.text((465, 215), weather.daily_forecast()["+72h"]["max"], fill=0, font=font14)
    display.draw_black.text((498, 215), "max", fill=0, font=font14)  # +72H MAX TEMPERATURE
    display.draw_black.text((465, 230), weather.daily_forecast()["+72h"]["pop"], fill=0, font=font14)
    display.draw_black.text((498, 230), "pluie", fill=0, font=font14)  # +72H RAIN PROBABILITY

    # +96h
    display.draw_black.text((360, 255), weather.daily_forecast()["+96h"]["date"], fill=0, font=font16)  # +96H DAY
    display.draw_icon(400, 275, "r", 50, 50,
                      weather.weather_description(weather.daily_forecast()["+96h"]["id"])[0])  # +96H WEATHER ICON
    display.draw_black.text((465, 275), weather.daily_forecast()["+96h"]["min"], fill=0, font=font14)
    display.draw_black.text((498, 275), "min", fill=0, font=font14)  # +96H MIN TEMPERATURE
    display.draw_black.text((465, 290), weather.daily_forecast()["+96h"]["max"], fill=0, font=font14)
    display.draw_black.text((498, 290), "max", fill=0, font=font14)  # +96H MAX TEMPERATURE
    display.draw_black.text((465, 305), weather.daily_forecast()["+96h"]["pop"], fill=0, font=font14)
    display.draw_black.text((498, 305), "pluie", fill=0, font=font14)  # +96H RAIN PROBABILITY

    ###################################################################################################################
    # GRAPHS
    # PRESSURE & TEMPERATURE
    pression = []
    temperature = []
    maxi = 440  # MAX VERT. PIXEL OF THE GRAPH
    mini = 360  # MIN VERT PIXEL OF THE GRAPH
    x = [55, 105, 155, 205, 255, 305, 355]  # X value of the points
    j = ["J-6", "J-5", "J-4", "J-3", "J-2", "J-1", "J"]  # LABELS


    weather.graph_p_t()
    data = weather.prevision[1]
    global been_reboot
    if (been_reboot == 1):
        try :
            file = open("saved.txt","r")
            weather.prevision[1] = json.loads(file.read())
            data = weather.prevision[1]
            been_reboot = 0
            file.close()
        except:
            pass

    else :
        pass

    file = open("saved.txt", "w")
    file.write(str(data))
    file.close()
    for i in range(len(data)):
        pression.append(data[i][0])
        temperature.append(data[i][1])

    # PRESSURE
    display.draw_black.line((40, mini, 40, maxi + 20), fill=0, width=1)  # GRAPH AXIS
    display.draw_black.text((10, mini), str(max(pression)), fill=0, font=font12)  # MAX AXIS GRAPH LABEL
    display.draw_black.text((10, maxi), str(min(pression)), fill=0, font=font12)  # MIN AXIS GRAPH LABEL
    display.draw_black.text((10, mini + (maxi - mini) // 2), str((max(pression) + min(pression)) // 2), fill=0,
                            font=font12)  # MID VALUE LABEL
    for i in range(len(x)):  # UPDATE CIRCLE POINTS
        display.draw_black.text((x[i], 455), j[i], fill=0, font=font12)
        display.draw_circle(x[i], map_resize(pression[i], min(pression), max(pression), maxi, mini), 3, "r")
    for i in range(len(x) - 1):  # UPDATE LINE
        display.draw_red.line((x[i], map_resize(pression[i], min(pression), max(pression), maxi, mini), x[i + 1],
                               map_resize(pression[i + 1], min(pression), max(pression), maxi, mini)), fill=0,
                              width=2)
    # TEMPERATURE
    display.draw_black.line((430, mini, 430, maxi + 20), fill=0, width=1)  # GRAPH AXIS
    display.draw_black.text((410, mini), str(max(temperature)), fill=0, font=font12)  # MAX AXIS GRAPH LABEL
    display.draw_black.text((410, maxi), str(min(temperature)), fill=0, font=font12)  # MIN AXIS GRAPH LABEL
    display.draw_black.text((410, mini + (maxi - mini) // 2), str((max(temperature) + min(temperature)) // 2), fill=0,
                            font=font12)  # MID VALUE LABEL
    for i in range(len(x)):  # UPDATE CIRCLE POINTS
        display.draw_black.text((x[i] + 400, 455), j[i], fill=0, font=font12)
        display.draw_circle(x[i] + 400, map_resize(temperature[i], min(temperature), max(temperature), maxi, mini), 3,
                            "r")
    for i in range(len(x) - 1):  # UPDATE LINE
        display.draw_red.line((x[i] + 400, map_resize(temperature[i], min(temperature), max(temperature), maxi, mini),
                               x[i + 1] + 400,
                               map_resize(temperature[i + 1], min(temperature), max(temperature), maxi, mini)),
                              fill=0, width=2)

    ###################################################################################################################
    # ALERT AND POLLUTION

    ###################################################################################################################
    # NEWS UPDATE
    news_selected = news.selected_title()
    display.draw_black.text((550, 15), "NEWS", fill=0, font=font24)
    for i in range(5):
        if len(news_selected) == 1:
            display.draw_black.text((550, 40), news_selected[0], fill=0, font=font14)
            break
        else:
            if len(news_selected[i]) <= 3 :
                for j in range(len(news_selected[i])):
                    display.draw_black.text((550, 40 + j * 15 + i * 60), news_selected[i][j], fill=0, font=font14)
            else:
                for j in range(2):
                    display.draw_black.text((550, 40 + j * 15 + i * 60), news_selected[i][j], fill=0, font=font14)
                display.draw_black.text((550, 40 + 2 * 15 + i * 60), news_selected[i][2] + "[.]", fill=0, font=font14)



    ###################################################################################################################
    logging.info("Updating screen.")
    # display.im_black.show()
    # display.im_red.show()  
    logging.info("\tPrinting.")

    time.sleep(2)
    epd.display(epd.getbuffer(display.im_black), epd.getbuffer(display.im_red))
    time.sleep(2)	
    return True

def main():
    global been_reboot
    been_reboot=1
    weather_data = False
    weather = Weather(lat, lon, api_key_weather)
    news = News(news_width)
    display = Display()
    if screen_size == "2.7in":
        logging.info("Initializing EPD for 2.7in")
        epd = epd2in7.EPD()
        weather_station_inst = weather_station(epd, weather, news)
        logging.info("Creating Buttons")
        btn1 = Button(5)
        btn1.when_pressed = weather_station_inst.button1
        btn2 = Button(6)
        btn2.when_pressed = weather_station_inst.button2
        btn3 = Button(13)
        btn3.when_pressed = weather_station_inst.button3
        btn4 = Button(19)
        btn4.when_pressed = weather_station_inst.button4
        while True:
            weather_station_inst = weather_station(epd, weather, news)
            weather_station_inst.draw2in7(epd)
            logging.info("Screen is drawn")
            logging.info("Going to sleep.")
            logging.info("------------")
            ran_once = True
            time.sleep(900)
    else:
        logging.info("Screen size is 7.5")
        epd = epd7in5b_V2.EPD()
        epd.init()
        epd.Clear(0xFF)
        logging.info("Drawing screen")
        Himage = Image.new('1', (epd.height, epd.width), 255)  # 255: clear the frame
        draw = ImageDraw.Draw(Himage)
        draw = draw7in5(epd,weather,news,display)
        epd.display(epd.getbuffer(Himage))
        logging.info("Screen is drawn")
        time.sleep(900)
    return True

if __name__ == "__main__":
   main()
