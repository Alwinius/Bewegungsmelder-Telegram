#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

import logging
import time
from bot.components.base import Session
from bot.components.user import User
from bot.components import config

from telegram import Chat, ParseMode, InlineKeyboardMarkup, InlineKeyboardButton, Bot
from telegram.error import ChatMigrated, TimedOut, Unauthorized, BadRequest

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)

default_reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Start", callback_data="H")]])


def send(bot, chat_id, message, reply_markup=default_reply_markup, message_id=None) -> bool:
    try:
        if message_id is None or message_id == 0:
            rep = bot.sendMessage(chat_id=chat_id, text=message, reply_markup=reply_markup,
                                  parse_mode=ParseMode.HTML)
            session = Session()
            user: User = session.query(User).filter(User.id == chat_id).first()
            user.message_id = rep.message_id
            session.commit()
            session.close()
            return True
        else:
            rep = bot.editMessageText(chat_id=chat_id, text=message, message_id=message_id, reply_markup=reply_markup,
                                      parse_mode=ParseMode.HTML)
            session = Session()
            user = session.query(User).filter(User.id == chat_id).first()
            user.message_id = rep.message_id
            session.commit()
            session.close()
            return True
    except (Unauthorized, BadRequest) as e:
        if "Message is not modified" in e.message:
            # user clicked on same button twice, not an issue
            return True
        session = Session()
        user = session.query(User).filter(User.id == chat_id).first()
        user.notifications = -1
        logging.exception(f"Error while sending message to {user.first_name} (#{chat_id})")
        send_developer_message(bot, f"Error while sending message to {user.first_name} (#{chat_id})\n\n{e}")
        session.commit()
        session.close()
        return True
    except TimedOut:
        time.sleep(5)  # delays for 5 seconds
        return send(bot, chat_id, message_id, message, reply_markup)
    except ChatMigrated as e:
        session = Session()
        user = session.query(User).filter(User.id == chat_id).first()
        user.id = e.new_chat_id
        session.commit()
        session.close()
        return True


def send_developer_message(bot: Bot, msg):
    fallback = config['AdminId']
    chat_ids = config.get('DeveloperIds', fallback).split(",")

    for chat_id in chat_ids:
        bot.send_message(text=msg, chat_id=chat_id)


def checkuser(chat: Chat):
    session = Session()
    entry = session.query(User).filter(User.id == chat.id).first()
    if not entry:
        # create entry
        new_user = User(id=chat.id, first_name=chat.first_name, last_name=chat.last_name, username=chat.username,
                        title=chat.title)
        session.add(new_user)
        session.commit()
        session.close()
    else:
        entry.counter += 1
        session.commit()
        session.close()
