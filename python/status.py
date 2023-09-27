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

sys.path.append("..")
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

logging.info("draw loading")

image0 = Image.new("RGB", (disp.width, disp.height), "BLACK")
image1 = Image.open(__path__ + "/Image/luis.png")
draw = ImageDraw.Draw(image0)
image0.paste(image1)
# image = Image.open(ImagePath[i])
# image = image.rotate(0)
disp.ShowImage(image0)
time.sleep(5)

logging.info("draw text")

while True:
    try:
        now = datetime.now()
        uptime = (
            subprocess.check_output("uptime", shell=True).decode("utf-8").split(",")[0]
        )
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
        cmd = "top -bn1 | grep load | awk '{printf \"Load: %.2f\", $(NF-2)}'"
        CPU = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "free -m | awk 'NR==2{printf \"%s/%s MB  %.2f%%\", $3,$2,$3*100/$2 }'"
        MemUsage = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = 'df -h | awk \'$NF=="/"{printf "Disk: %d/%d GB  %s", $3,$2,$5}\''
        Disk = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "cat /sys/class/thermal/thermal_zone0/temp |  awk '{printf \"T: %.1f C\", $(NF-0) / 1000}'"  # pylint: disable=line-too-long
        Temp = subprocess.check_output(cmd, shell=True).decode("utf-8")
        cmd = "sudo cat /etc/wpa_supplicant/wpa_supplicant.conf | grep ssid="
        SSID = subprocess.check_output(cmd, shell=True).decode("utf-8").split('"')
        lines = [
            {
                "label": "",
                "labelColor": "GREEN",
                "value": "Hostname: " + Hostname,
                "valueColor": "WHITE",
                "labelFont": Font20,
                "valueFont": Font18,
                "innerMargin": 25,
                "marginBottom": 20,
            },
            {
                "label": "",
                "labelColor": "GREEN",
                "value": "SSID: " + SSID[1],
                "valueColor": "WHITE",
                "labelFont": Font20,
                "valueFont": Font18,
                "innerMargin": 25,
                "marginBottom": 20,
            },
            {
                "label": "Up Time",
                "labelColor": "GREEN",
                "value": uptime.split("up ")[1],
                "valueColor": "LIGHTGRAY",
                "labelFont": Font20,
                "valueFont": Font18,
                "innerMargin": 25,
                "marginBottom": 20,
            },
            {
                "label": "Internal IP",
                "labelColor": "GREEN",
                "value": IP,
                "valueColor": "LIGHTGRAY",
                "labelFont": Font20,
                "valueFont": Font18,
                "innerMargin": 25,
                "marginBottom": 20,
            },
            {
                "label": "External IP",
                "labelColor": "GREEN",
                "value": IP_EXT,
                "valueColor": "LIGHTGRAY",
                "labelFont": Font20,
                "valueFont": Font18,
                "innerMargin": 25,
                "marginBottom": 20,
            },
            {
                "label": "CPU",
                "labelColor": "GREEN",
                "value": Temp + " " + CPU,
                "valueColor": "LIGHTGRAY",
                "labelFont": Font20,
                "valueFont": Font18,
                "innerMargin": 25,
                "marginBottom": 20,
            },
            {
                "label": "Memory / Storage",
                "labelColor": "GREEN",
                "value": MemUsage + "\n" + Disk,
                "valueColor": "LIGHTGRAY",
                "labelFont": Font20,
                "valueFont": Font18,
                "innerMargin": 25,
                "marginBottom": 45,
            },
        ]
        lineY = 5
        draw.text((90, lineY), now.strftime("%H:%M:%S"), fill="ORANGE", font=Font20)
        lineY = 30
        for line in lines:
            if line["label"]:
                draw.text(
                    (5, lineY),
                    line["label"],
                    fill=line["labelColor"],
                    font=line["labelFont"],
                )
                lineY = lineY + line["innerMargin"]
            if line["value"]:
                draw.text(
                    (5, lineY),
                    line["value"],
                    fill=line["valueColor"],
                    font=line["valueFont"],
                )
                lineY = lineY + line["marginBottom"]
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
