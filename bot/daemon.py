#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

import logging
from typing import List
from bot.messaging import checkuser, send
from bot.components import config
from bot.components.base import Base, Session, engine
from bot.components.event import Event
from bot.components.user import User
from bot.components.category import Category
from datetime import datetime, timedelta
from copy import deepcopy

from sqlalchemy import and_, func
from telegram.ext import CallbackContext, Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, Message

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def get_filter_overview(user_id: int):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    msg = "Du siehst aktuell folgende Kategorien:\n"
    for cat in Category:
        if cat in user.selected_categories:
            msg += "✅ " + cat + "\n"
        else:
            msg += "🚫 " + cat + "\n"
    msg += "und diese Gruppen:\n"
    session.close()
    return msg


def get_events(date: int, chat_id: int) -> str:
    events_today = False
    selected_date = datetime.today() + timedelta(days=date)
    if date == 0:
        print_day = "heute"
    elif date == 1:
        print_day = "morgen"
    else:
        print_day = "am " + selected_date.strftime("%a, %d.%m.")
    msg = "Folgende Veranstaltungen finden " + print_day + " statt:\n"
    session = Session()
    events = session.query(Event).filter(and_(func.date(Event.start) <= selected_date.date(),
                                              func.date(Event.end) >= selected_date.date()))
    user = session.query(User).filter(User.id == chat_id).first()
    for event in events:
        if event.event_category in user.selected_categories:
            events_today = True
            msg += str(event)
    session.close()
    if events_today:
        return msg
    else:
        return "Leider finden " + print_day + " keine Veranstaltungen statt."


def process_categories(chat_id: int, args: list) -> [str, InlineKeyboardMarkup]:
    session = Session()
    user = session.query(User).filter(User.id == chat_id).first()
    if len(args) > 2:
        cat: Category = Category[args[2]]
        selected_categories = deepcopy(user.selected_categories)
        if args[1] == "1" and cat.value not in user.selected_categories:  # this means enable
            selected_categories.append(cat)
            user.selected_categories = selected_categories
            session.commit()
        elif args[1] == "0" and cat.value in user.selected_categories:  # this means disable
            logging.debug("removing item from categories")
            selected_categories.remove(cat)
            user.selected_categories = selected_categories
            session.commit()
    msg = "Du siehst aktuell folgende Kategorien:\n"
    first_element = True
    btns = []
    for cat in Category:
        if cat in user.selected_categories:
            msg += "✅ " + cat + "\n"
            btn = InlineKeyboardButton(cat, callback_data="2$0$" + cat.name)
            if first_element:
                btns.append([btn])
                first_element = False
            else:
                btns[-1].append(btn)
                first_element = True
        else:
            msg += "🚫 " + cat + "\n"
            btn = InlineKeyboardButton(cat, callback_data="2$1$" + cat.name)
            if first_element:
                btns.append([btn])
                first_element = False
            else:
                btns[-1].append(btn)
                first_element = True
    btns.append([InlineKeyboardButton("Veranstaltungen", callback_data="0$0"), InlineKeyboardButton("Gruppen filtern", callback_data="1")])
    session.close()

    return msg, InlineKeyboardMarkup(btns)


# Handlers
def start(update: Update, context: CallbackContext, message_id=None):
    checkuser(update.message.chat)
    msg = "Willkommen beim Telegram-Bot des Bewegungsmelders. Über die Buttons unten kannst du nach aktuellen " \
          "Veranstaltungen suchen und deine Benachrichtigungen verwalten. Informationen über diesen Bot gibt's hier " \
          "/about. "
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Aktuelle Veranstaltungen", callback_data="0$0")],
                                         [InlineKeyboardButton("Benachrichtigungen", callback_data="3"),
                                          InlineKeyboardButton("Filter", callback_data="4")]])
    send(context.bot, update.message.chat_id, msg, reply_markup, message_id)


def about(update: Update, context: CallbackContext):
    checkuser(update.message.chat)
    msg = ("Dieser Bot wurde von @Alwinius entwickelt.\n"
           "Der Quellcode ist unter https://github.com/Alwinius/Bewegungsmelder-Telegram verfügbar.\n"
           "Weitere interessante Bots: \n - "
           "@mydealz\\_bot\n - @aachenmensabot")
    print(msg)
    send(context.bot, update.message.chat_id, msg)


def inline_callback(update: Update, context: CallbackContext):
    message: Message = update.callback_query.message
    checkuser(message.chat)
    args: List[str] = update.callback_query.data.split("$")
    # message structure: ID$payload
    # ID: H - Home
    #     0 - list events according to saved filters, payload: day
    #     1 - modify groups, payload: id, enable 1 /disable 0 - TODO
    #     2 - modify event categories: id, enable 1 /disable 0
    #     3 - modify notifications: to be defined - TODO
    #     4 - filter overview

    if args[0] == "H":
        start(update.callback_query, context, message.message_id)
    elif args[0] == "0":
        msg = get_events(int(args[1]), message.chat.id)
        if args[1] == "0":
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton(">", callback_data="0$1")],
                 [InlineKeyboardButton("Start", callback_data="H"), InlineKeyboardButton("Filter", callback_data="4")]])
        else:
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("<", callback_data="0$" + str(int(args[1]) - 1)),
                  InlineKeyboardButton(">", callback_data="0$" + str(int(args[1]) + 1))],
                 [InlineKeyboardButton("Start", callback_data="H"), InlineKeyboardButton("Filter", callback_data="4")]])

        send(context.bot, message.chat.id, msg, reply_markup, message_id=message.message_id)
    elif args[0] == "4":
        msg = get_filter_overview(message.chat.id)
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Gruppen filtern", callback_data="1"),
              InlineKeyboardButton("Kategorien filtern", callback_data="2")],
             [InlineKeyboardButton("Veranstaltungen", callback_data="0$0")]])
        send(context.bot, message.chat.id, msg, reply_markup, message_id=message.message_id)
    elif args[0] == "2":
        msg, reply_markup = process_categories(message.chat.id, args)
        send(context.bot, message.chat.id, msg, reply_markup, message_id=message.message_id)
    else:
        logging.error("unknown inline command")
        msg = "Kommando nicht erkannt"
        send(context.bot, message.chat_id, msg, message_id=message.message_id)

    # if int(args[0]) > 400:
    #     # show mealplan
    #     mensa_id, mensa_name = args
    #     noti, presel = checkuser(message.chat, sel=mensa_id)
    #
    #     if int(noti) <= 0 or int(noti) != int(mensa_id):
    #         noti_btn = InlineKeyboardButton("Auto-Update aktivieren", callback_data="5$1")
    #     else:
    #         noti_btn = InlineKeyboardButton("Auto-Update deaktivieren", callback_data="5$0")
    #
    #     msg = menu_manager.get_menu(int(mensa_id)).get_meals_message()
    #     reply_markup = InlineKeyboardMarkup([[noti_btn]] + button_list)
    #     send(context.bot, message.chat_id, msg, reply_markup=reply_markup, message_id=message.message_id)
    # elif int(args[0]) == 5 and len(args) > 1:
    #     # manage notifications
    #     noti, presel = checkuser(message.chat)
    #     enabled = args[1] == "1"
    #     change_notifications(message.chat, presel, enabled)
    #
    #     if enabled:
    #         noti_btn = InlineKeyboardButton("Auto-Update deaktivieren", callback_data="5$0")
    #         msg = "Auto-Update aktiviert für Mensa " + MENSEN[int(presel)]
    #     else:
    #         noti_btn = InlineKeyboardButton("Auto-Update aktivieren", callback_data="5$1")
    #         msg = "Auto-Update deaktiviert"
    #
    #     reply_markup = InlineKeyboardMarkup([[noti_btn]] + button_list)
    #     send(context.bot, message.chat_id, msg, reply_markup=reply_markup, message_id=message.message_id)
    # else:

    # dev_msg = f"Inlinekommando nicht erkannt.\n\nData: {update.callback_query.data}\nUser:{message.chat}"
    # send_developer_message(context.bot, dev_msg)


# def send_notifications(bot=None):
#     if bot is None:
#         bot = Bot(token=config['BotToken'])
#
#     plans = {}
#     for mensa_id, mensa_name in MENSEN.items():
#         print(f"Getting plan for {mensa_name} (#{mensa_id})")
#         plans[mensa_id] = menu_manager.get_menu(mensa_id)
#
#     noti_btn = InlineKeyboardButton("Auto-Update deaktivieren", callback_data="5$0")
#     reply_markup = InlineKeyboardMarkup([[noti_btn]] + button_list)
#
#     session = Session()
#     users = session.query(User).filter(User.notifications > 0)
#     for user in users:
#         user.counter += 1
#         session.commit()
#         try:
#             print("Sending plan to", user.first_name)
#             send(bot, user.id, plans[int(user.notifications)].get_meals_message(),
#                  reply_markup=reply_markup, message_id=user.message_id)
#         except TypeError:
#             logging.exception(f"Caught TypeError while processing user {user.first_name}")
#
#     session.close()


# def job_callback(context: CallbackContext):
#     logging.debug("Scheduled notification update triggered")
#     send_notifications(bot=context.bot)


def run_daemon():
    Base.metadata.create_all(engine)

    updater = Updater(token=config["BotToken"], use_context=True)
    dispatcher = updater.dispatcher

    start_handler = CommandHandler('start', start)
    dispatcher.add_handler(start_handler)
    about_handler = CommandHandler('about', about)
    dispatcher.add_handler(about_handler)
    inline_handler = CallbackQueryHandler(inline_callback)
    dispatcher.add_handler(inline_handler)
    fallback_handler = MessageHandler(Filters.all, start)
    dispatcher.add_handler(fallback_handler)

    # schedule daily update
    # hour = int(config.get('NotificationHour', 16))
    # first = datetime.time(hour=hour, minute=0)
    # now = datetime.datetime.now()
    # logging.info(f"Job will run daily at {first}. Server time is {now.strftime('%H:%M:%S')}.")
    # updater.job_queue.run_daily(job_callback, time=first)

    webhook_url = config.get('WebhookUrl', "").strip()
    if len(webhook_url) > 0:
        updater.bot.set_webhook(webhook_url)
        updater.start_webhook(
            listen=config.get('Host', 'localhost'),
            port=config.get('Port', 4215),
            webhook_url=webhook_url)
    else:
        # use polling if no webhook is set
        updater.start_polling()

    updater.idle()
    updater.stop()
