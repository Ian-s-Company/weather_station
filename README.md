# Current and Forecast Weather Display Station
This project is derived from, but significantly enhanmced from a weather station described here:

https://www.hackster.io/aerodynamics/weather-and-news-station-e-paper-and-raspberry-pi-a19fa3

You will need:
- Raspberry Pi Zero 2 W or a more powerful Raspberry Pi
- Waveshare 2.7in E-paper display with 4 buttons
- MicroSD card (I used a 32GB SanDisk Ultra)
- USB Keyboard (to plug into the Raspberry Pi to configure OS)
- Laptop (to format SD Card with Raspberry Pi image and run Github runner on WSL)

The documentation is for a Raspberry Pi Zero 2 W with soldered pins. You can get one without soldered pins as well if you have the appropriate equipment and expertise. 
As far as I know it won't run on anything other than a Raspberry Pi since it needs the proper GPIO socket.

I made changes to allow for a 2.7in (254x176) or a 7.5in (800x480) Waveshare e-ink display.

- https://www.waveshare.com/product/raspberry-pi/displays/e-paper/2.7inch-e-paper-hat.htm
- https://www.waveshare.com/product/raspberry-pi/displays/e-paper/7.5inch-e-paper-hat-b.htm

I also set up a process to download weather icons if needed.

Steps
1. Format MicroSD card and install Ubuntu OS
2. Plugin MicroSD to laptop. 
3. Download and Install Raspberry Pi Installer (https://www.raspberrypi.com/software/)
4. Execute Installer
5. Select correct Raspberry Pi Device, OS, and Storage
6. Modify OS Customization as desired. I recommend setting locale, SSID, username, name, Enable SSD (public-key only and capture the key) to what makes sense for you.
7. Save Settings and continue
8. Configure OS on Raspberry Pi
9. Configure Github Runner on Windows WSL and connection to Raspberry Pi
10. Install E-Paper Display on Raspberry Pi
11. Run Deploy process to setup Weather Display
