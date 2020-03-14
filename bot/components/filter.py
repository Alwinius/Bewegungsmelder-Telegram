#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

import logging
from copy import deepcopy

from telegram import InlineKeyboardMarkup, InlineKeyboardButton

from bot.components.base import Session
from bot.components.category import Category
from bot.components.group import Group
from bot.components.user import User


def get_filter_overview(user_id: int):
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    msg = "Du siehst aktuell folgende Kategorien:\n"
    for cat in Category:
        if cat in user.selected_categories:
            msg += "📣 " + cat.value + "\n"
        else:
            msg += "🚫 " + cat.value + "\n"
    msg += "und diese Gruppen:\n"
    groups = session.query(Group)
    for group in groups:
        if group in user.excluded_groups:
            msg += "🚫 " + group.name + "\n"
        else:
            msg += "📣 " + group.name + "\n"
    session.close()
    return msg


def process_groups(user_id: int, args: list) -> [str, InlineKeyboardMarkup]:
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if len(args) > 2:
        group_id = int(args[2])
        group = session.query(Group).filter(Group.id == group_id).first()
        if group is not None:
            if args[1] == "1" and group in user.excluded_groups: # this means show the group
                user.excluded_groups.remove(group)
                session.commit()
            if args[1] == "0" and group not in user.excluded_groups:  # this means exclude the group
                user.excluded_groups.append(group)
                session.commit()
    msg = "Du siehst aktuell folgende Gruppen:\n"
    first_element = True
    btns = []
    groups = session.query(Group)
    for group in groups:
        if group in user.excluded_groups:
            btn = InlineKeyboardButton("🔇 "+group.name, callback_data="1$1$" + str(group.id))
            msg += "🔇 " + group.name + "\n"
        else:
            btn = InlineKeyboardButton("📣 "+group.name, callback_data="1$0$" + str(group.id))
            msg += "📣 " + group.name + "\n"

        if first_element:
            btns.append([btn])
            first_element = False
        else:
            btns[-1].append(btn)
            first_element = True
    btns.append([InlineKeyboardButton("📅 Veranstaltungen", callback_data="0$0"),
                 InlineKeyboardButton("📚 Kategorien filtern", callback_data="2")])
    session.close()
    return msg, InlineKeyboardMarkup(btns)


def process_categories(user_id: int, args: list) -> [str, InlineKeyboardMarkup]:
    session = Session()
    user = session.query(User).filter(User.id == user_id).first()
    if len(args) == 2: # handling of ALL button
        if args[1] == "NONE":
            user.selected_categories = []
            session.commit()
        elif args[1] == "ALL":
            user.selected_categories = [e for e in Category]
            session.commit()
    elif len(args) > 2:
        cat: Category = Category[args[2]]
        selected_categories = deepcopy(user.selected_categories)
        if args[1] == "1" and cat not in user.selected_categories:  # this means enable
            selected_categories.append(cat)
            user.selected_categories = selected_categories
            session.commit()
        elif args[1] == "0" and cat in user.selected_categories:  # this means disable
            logging.debug("removing item from categories")
            selected_categories.remove(cat)
            user.selected_categories = selected_categories
            session.commit()
    msg = "Du siehst aktuell folgende Kategorien:\n"
    first_element = True
    btns = []
    all_activated = True
    for cat in Category:
        if cat in user.selected_categories:
            msg += "📣 " + cat.value + "\n"
            btn = InlineKeyboardButton("📣 "+cat.value, callback_data="2$0$" + cat.name)
        else:
            all_activated=False
            msg += "🔇 " + cat.value + "\n"
            btn = InlineKeyboardButton("🔇 "+cat.value, callback_data="2$1$" + cat.name)

        if first_element:
            btns.append([btn])
            first_element = False
        else:
            btns[-1].append(btn)
            first_element = True
    # special handling of the "Alle" button
    if all_activated:
        btn = InlineKeyboardButton("📣 Alle", callback_data="2$NONE")
    else:
        btn = InlineKeyboardButton("🔇 Alle", callback_data="2$ALL")
    if first_element:
        btns.append(btn)
    else:
        btns[-1].append(btn)
    btns.append([InlineKeyboardButton("📅 Veranstaltungen", callback_data="0$0"),
                 InlineKeyboardButton("👯 Gruppen filtern", callback_data="1")])
    session.close()

    return msg, InlineKeyboardMarkup(btns)