#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

from bot.components.base import Base, engine
import telegram
import configparser
from bot.daemon import get_events

config = configparser.ConfigParser()
config.read('config.ini')
Base.metadata.create_all(engine)

msg = get_events(0, config['DEFAULT']['AdminId'])
if "Leider finden" not in msg:
    print(msg)
    bot = telegram.Bot(token=config['DEFAULT']['BotToken'])
    ret = bot.send_message(chat_id=config['DEFAULT']['TodayChannel'], text=msg, parse_mode=telegram.ParseMode.HTML, disable_web_page_preview=True)
