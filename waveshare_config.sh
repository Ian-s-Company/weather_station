#!/usr/bin/sh
#
apt update; apt -y upgrade
apt install python3-venv
cd ~/; python -m venv weather_station_venv
source weather_station_venv/bin/activate
pip install requests pillow gpiozero pytest;
cd /tmp
if [ -d '/tmp/waveshare' ]; then rm -Rf /tmp/waveshare; fi
mkdir -p /tmp/waveshare
cd waveshare
wget https://github.com/joan2937/lg/archive/master.zip
wget http://www.airspayce.com/mikem/bcm2835/bcm2835-1.71.tar.gz
wget https://project-downloads.drogon.net/wiringpi-latest.deb
git clone https://github.com/WiringPi/WiringPi
unzip master.zip
tar zxvf bcm2835-1.71.tar.gz
cd /tmp/waveshare/lg-master
make
make install
apt install gpiod libgpiod-dev wiringpi
cd /tmp/waveshare/bcm2835-1.71/
./configure && make && make check && make install
dpkg -i wiringpi-latest.deb
gpio -v
cd /tmp/waveshare/WiringPi
./build
gpio -v
