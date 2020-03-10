#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

import requests
from bs4 import BeautifulSoup
from event import Event
import telegram
import configparser

page = requests.get("https://bewegungsmelder-aachen.de/kalender")
soup = BeautifulSoup(page.content, "lxml")
events = soup.select(".post-column")
events_today = False
msg = "Folgende Veranstaltungen finden heute statt:\n"

for event in events:
    e = Event(event)
    if e.is_today():
        events_today = True
        msg += str(e)

if events_today:
    print(msg)
    config = configparser.ConfigParser()
    config.read('config.ini')
    bot = telegram.Bot(token=config['DEFAULT']['BotToken'])
    ret = bot.send_message(chat_id=config['DEFAULT']['TodayChannel'], text=msg, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)

