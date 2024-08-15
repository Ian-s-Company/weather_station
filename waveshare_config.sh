#!/usr/bin/sh
#
apt update; apt -y upgrade
apt install python3-pip python3-pil python3-numpy python3-gpiozero  python3-RPi.GPIO python3-spidev
cd /tmp
if [ -d '/tmp/waveshare' ]; then rm -Rf /tmp/waveshare; fi
mkdir -p /tmp/waveshare
cd waveshare
git clone https://github.com/waveshare/e-Paper.git
wget https://files.waveshare.com/upload/7/71/E-Paper_code.zip
unzip E-Paper_code.zip -d e-Paper
cd e-Paper/RaspberryPi_JetsonNano/
cd python/examples
#python3 epd_2in7_V2_test.py
