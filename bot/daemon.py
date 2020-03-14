#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

from datetime import datetime, timedelta, time
from typing import List

from sqlalchemy import and_, func
from telegram import Update, Message, Bot
from telegram.ext import CallbackContext, Updater, CommandHandler, CallbackQueryHandler, Filters, MessageHandler

from bot.components import config
from bot.components.base import Base, engine
from bot.components.event import Event
from bot.components.filter import *
from bot.components.schedule import Schedule
from bot.messaging import checkuser, send, send_developer_message
from bot.scraper import Scraper

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.DEBUG)


def process_notifications(user_id: int, args: list):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if len(args) > 1:
        new_notification: Schedule = Schedule[args[1]]
        if new_notification != user.notify_schedule:
            user.notify_schedule = new_notification
            session.commit()
    msg = "Du bekommst aktuell " + str(
        user.notify_schedule.value) + "eine Benachrichtigung über Veranstaltungen passend zu " \
                                      "deinen Filtereinstellungen."
    session.close()
    return msg


def get_events(date: int, chat_id: int) -> [str, bool]:
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
        if event.event_category in user.selected_categories and event.group not in user.excluded_groups:
            events_today = True
            msg += str(event)
    session.close()
    if events_today:
        return msg, True
    else:
        return "Leider finden " + print_day + " keine Veranstaltungen statt.", False


# Handlers
def start(update: Update, context: CallbackContext, message_id=None):
    checkuser(update.message.chat)
    msg = "Willkommen beim Telegram-Bot des Bewegungsmelders. Über die Buttons unten kannst du nach aktuellen " \
          "Veranstaltungen suchen und deine Benachrichtigungen verwalten. Informationen über diesen Bot gibt's hier " \
          "/about. "
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("📅 Veranstaltungen", callback_data="0$0")],
                                         [InlineKeyboardButton("⏰ Benachrichtigungen", callback_data="3"),
                                          InlineKeyboardButton("🗂️ Filter", callback_data="4")]])
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
    #     1 - modify groups, payload: id, show 1 /exclude 0
    #     2 - modify event categories: id, enable 1 /disable 0
    #     3 - modify notifications: Schedule.name
    #     4 - filter overview

    if args[0] == "H":
        start(update.callback_query, context, message.message_id)
    elif args[0] == "0":
        msg, _ = get_events(int(args[1]), message.chat.id)
        if args[1] == "0":
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("➡️", callback_data="0$1")],
                 [InlineKeyboardButton("🏡 Start", callback_data="H"), InlineKeyboardButton("🗂️ Filter", callback_data="4")]])
        else:
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("⬅️", callback_data="0$" + str(int(args[1]) - 1)),
                  InlineKeyboardButton("➡️", callback_data="0$" + str(int(args[1]) + 1))],
                 [InlineKeyboardButton("🏡 Start", callback_data="H"), InlineKeyboardButton("🗂️ Filter", callback_data="4")]])

        send(context.bot, message.chat.id, msg, reply_markup, message_id=message.message_id)
    elif args[0] == "4":
        msg = get_filter_overview(message.chat.id)
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("👯 Gruppen filtern", callback_data="1"),
              InlineKeyboardButton("📚 Kategorien filtern", callback_data="2")],
             [InlineKeyboardButton("📅 Veranstaltungen", callback_data="0$0")]])
        send(context.bot, message.chat.id, msg, reply_markup, message_id=message.message_id)
    elif args[0] == "1":
        msg, reply_markup = process_groups(message.chat.id, args)
        send(context.bot, message.chat.id, msg, reply_markup, message_id=message.message_id)
    elif args[0] == "2":
        msg, reply_markup = process_categories(message.chat.id, args)
        send(context.bot, message.chat.id, msg, reply_markup, message_id=message.message_id)
    elif args[0] == "3":
        msg = process_notifications(message.chat.id, args)
        reply_markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("⏰ tägliche Benachrichtigungen", callback_data="3$" + Schedule.DAILY.name)],
             [InlineKeyboardButton("📅 wöchentliche Benachrichtigungen", callback_data="3$" + Schedule.WEEKLY.name)],
             [InlineKeyboardButton("🔭 keine Benachrichtigungen", callback_data="3$" + Schedule.NONE.name)],
             [InlineKeyboardButton("📅 Veranstaltungen", callback_data="0$0"),
              InlineKeyboardButton("🗂️ Filter", callback_data="4")]])
        send(context.bot, message.chat.id, msg, reply_markup, message_id=message.message_id)
    else:
        logging.error("unknown inline command")
        msg = "Kommando nicht erkannt"
        send(context.bot, message.chat_id, msg, message_id=message.message_id)
        dev_msg = f"Inlinekommando nicht erkannt.\n\nData: {update.callback_query.data}\nUser:{message.chat}"
        send_developer_message(context.bot, dev_msg)


def send_daily_notifications(bot=None):
    if bot is None:
        bot = Bot(token=config['BotToken'])

    reply_markup = InlineKeyboardMarkup(
        [[InlineKeyboardButton("📅 Veranstaltungen", callback_data="0$0"),
          InlineKeyboardButton("⏰ Benachrichtigungen ändern", callback_data="3")]])

    session = Session()
    users = session.query(User).filter(User.notify_schedule == Schedule.DAILY)
    for user in users:
        user.counter += 1
        session.commit()
        msg, events = get_events(0, user.id)
        if events:
            send(bot, user.id, msg,
                 reply_markup=reply_markup)
    session.close()


def daily_notification_callback(context: CallbackContext):
    logging.debug("Scheduled daily notifications triggered")
    send_daily_notifications(bot=context.bot)


def scraper_callback(context: CallbackContext = None):
    logging.debug("Scraping triggered")
    Scraper.start_scraping()


def run_daemon():
    Base.metadata.create_all(engine)

    updater: Updater = Updater(token=config["BotToken"], use_context=True)
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
    now = datetime.now()
    hour = int(config.get('NotificationHour', 0))
    first = time(hour=hour, minute=1, tzinfo=now.tzinfo)
    logging.info(f"Job will run daily at {first}. UTC time is {now.strftime('%H:%M:%S')}.")
    updater.job_queue.run_daily(daily_notification_callback, time=first)

    # the scraper will run every 5 hours
    updater.job_queue.run_repeating(scraper_callback, timedelta(hours=5))

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
