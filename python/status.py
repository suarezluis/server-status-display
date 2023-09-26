#!/usr/bin/python
# -*- coding: UTF-8 -*-
# import chardet
import os
import sys
import time
import logging
import subprocess
import spidev as SPI
from datetime import datetime

sys.path.append(".")
from lib import LCD_1inch9
from PIL import Image, ImageDraw, ImageFont

# Raspberry Pi pin configuration:
RST = 27
DC = 25
BL = 18
bus = 0
device = 0
logging.basicConfig(level=logging.DEBUG)


__path__ = os.path.dirname(__file__)

Font14 = ImageFont.truetype(__path__ + "/Font/Font02.ttf", 14)
Font15 = ImageFont.truetype(__path__ + "/Font/Font02.ttf", 15)
Font16 = ImageFont.truetype(__path__ + "/Font/Font02.ttf", 16)
Font17 = ImageFont.truetype(__path__ + "/Font/Font02.ttf", 17)
Font18 = ImageFont.truetype(__path__ + "/Font/Font02.ttf", 18)
Font19 = ImageFont.truetype(__path__ + "/Font/Font02.ttf", 19)
Font20 = ImageFont.truetype(__path__ + "/Font/Font02.ttf", 20)
Font21 = ImageFont.truetype(__path__ + "/Font/Font02.ttf", 21)
Font22 = ImageFont.truetype(__path__ + "/Font/Font02.ttf", 22)
Font23 = ImageFont.truetype(__path__ + "/Font/Font02.ttf", 23)
Font24 = ImageFont.truetype(__path__ + "/Font/Font02.ttf", 24)

# display with hardware SPI:
""" Warning!!!Don't  creation of multiple displayer objects!!! """
# disp = LCD_1inch9.LCD_1inch9(spi=SPI.SpiDev(bus, device),spi_freq=10000000,rst=RST,dc=DC,bl=BL)
disp = LCD_1inch9.LCD_1inch9()
# Initialize library.
disp.Init()
# Clear display.
disp.clear()
is_first_loop = True

logging.info("draw text")

while True:
    try:
        now = datetime.now()
        current_minutes_seconds = now.strftime("%M:%S")

        # Create blank image for drawing.
        image1 = Image.new("RGB", (disp.width, disp.height), "BLACK")
        draw = ImageDraw.Draw(image1)

        cmd = "hostname"
        Hostname = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "hostname -I | cut -d' ' -f1"
        IP = subprocess.check_output(cmd, shell=True).decode("utf-8")
        # Only pull external ip every hour
        if current_minutes_seconds == "00:00" or is_first_loop:
            cmd = "curl -s icanhazip.com"
            IP_EXT = subprocess.check_output(cmd, shell=True).decode("utf-8")

        cmd = "top -bn1 | grep load | awk '{printf \"CPU Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "free -m | awk 'NR==2{printf \"%s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
        Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"CPU Temp: %.1f C\", $(NF-0) / 1000}'"  # pylint: disable=line-too-long
        Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "sudo cat /etc/wpa_supplicant/wpa_supplicant.conf | grep ssid="
        SSID = subprocess.check_output(cmd, shell=True).decode("utf-8").split('"')

        lines = [
            {
                "label": "Internal IP",
                "labelColor": "GREEN",
                "value": IP,
                "valueColor": "YELLOW",
                "font": Font20,
            },
            {
                "label": "Hostname: " + Hostname,
                "labelColor": "LIGHTGRAY",
                "value": "",
                "valueColor": "",
                "font": Font24,
            },
            {
                "label": "External IP",
                "labelColor": "GREEN",
                "value": IP_EXT,
                "valueColor": "YELLOW",
                "font": Font22,
            },
            {
                "label": Temp,
                "labelColor": "LIGHTBLUE",
                "value": "",
                "valueColor": "YELLOW",
                "font": Font20,
            },
            {
                "label": CPU,
                "labelColor": "ORANGE",
                "value": "",
                "valueColor": "YELLOW",
                "font": Font20,
            },
            {
                "label": "Memory",
                "labelColor": "GREEN",
                "value": MemUsage,
                "valueColor": "YELLOW",
                "font": Font16,
            },
            {
                "label": Disk,
                "labelColor": "GREEN",
                "value": "",
                "valueColor": "YELLOW",
                "font": Font19,
            },
            {
                "label": "SSID: " + SSID[1],
                "labelColor": "BLUE",
                "value": "",
                "valueColor": "YELLOW",
                "font": Font22,
            },
        ]
        lineY = 5
        draw.text((95, lineY), now.strftime("%H:%M:%S"), fill="RED", font=Font22)
        lineY = 30
        for line in lines:
            draw.text(
                (5, lineY), line["label"], fill=line["labelColor"], font=line["font"]
            )
            lineY = lineY + 25
            if line["value"]:
                draw.text(
                    (5, lineY),
                    line["value"],
                    fill=line["valueColor"],
                    font=line["font"],
                )
                lineY = lineY + 25

        image1 = image1.rotate(0)
        disp.ShowImage(image1)
        is_first_loop = False
        time.sleep(1)

    except IOError as e:
        logging.info(e)
    except KeyboardInterrupt:
        disp.module_exit()

        logging.info("quit:")
        exit()
