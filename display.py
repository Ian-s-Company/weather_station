# -*- coding:utf-8 -*-

from PIL import Image, ImageDraw, ImageFont

home_dir = "/home/pi/weather_station/"
#font_choice = 7
font_choice = 4
if font_choice == 1:
    project_font = "font/Architects_Daughter/ArchitectsDaughter-Regular.ttf"
elif font_choice == 2:
    project_font = home_dir + "font/Inconsolata/static/Inconsolata-SemiBold.ttf"
elif font_choice == 3:
    project_font = "font/Comfortaa/static/Comfortaa-Light.ttf"
elif font_choice == 4:
    project_font = "font/Open_Sans/OpenSans-SemiBold.ttf"
elif font_choice == 5:
    project_font = "font/Roboto/Roboto-Regular.ttf"
elif font_choice == 6:
    project_font = "font/Roboto_Slab/static/RobotoSlab-Regular.ttf"
elif font_choice == 7:
    project_font = "font/Ubuntu_Mono/UbuntuMono-Bold.ttf"
else:
    project_font = "font/Open_Sans/OpenSans-SemiBold.ttf"


font8 = ImageFont.truetype(project_font, 8)
font12 = ImageFont.truetype(project_font, 12)
font14 = ImageFont.truetype(project_font, 14)
font16 = ImageFont.truetype(project_font, 16)
font20 = ImageFont.truetype(project_font, 20)
font24 = ImageFont.truetype(project_font, 24)
font36 = ImageFont.truetype(project_font, 36)
font48 = ImageFont.truetype(project_font, 48)


class Display:
    def __init__(self):
        self.im_black = Image.new('1', (800, 480), 255)
        self.im_red = Image.new('1', (800, 480), 255)
        self.draw_black = ImageDraw.Draw(self.im_black)
        self.draw_red = ImageDraw.Draw(self.im_red)

    def draw_circle(self, x, y, r, c):
        if c == "b":
            self.draw_black.ellipse((x - r, y - r, x + r, y + r), fill=0)
        else:
            self.draw_red.ellipse((x - r, y - r, x + r, y + r), fill=0)

    def draw_icon(self, x, y, number_of_colors, l, h, icon):
        # X cordinate
        # Y cordinate
        # # of colors (red and black or just black)
        # length of image
        # height of image
        # icon filename
        im_icon = Image.open("icons/" + icon + ".png")
        # im_icon = im_icon.convert("LA")
        im_icon = im_icon.resize((l, h))
        if number_of_colors == "2":
            self.im_black.paste(im_icon, (x, y), im_icon)
        else:
            self.im_red.paste(im_icon, (x, y), im_icon)

    def draw_icon_monochrome(self, x, y, l, h, icon):
        im_icon = Image.open("icons/" + icon + ".bmp")
        # im_icon = im_icon.convert("LA")
        im_icon = im_icon.resize((l, h))
