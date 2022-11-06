#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

from datetime import datetime, time
from sqlalchemy import Column, Enum, DateTime, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from bot.components.category import Category
import re
from bot.components.base import Base
import logging


class Event(Base):
    __tablename__ = 'event'
    event_name = Column(String())
    event_url = Column(String(), primary_key=True)
    event_category = Column(Enum(Category))
    start = Column(DateTime())
    end = Column(DateTime())
    has_time = Column(Boolean())
    group_id = Column(String(), ForeignKey('group.url_id'))
    group = relationship("Group", back_populates="events")
    excerpt = Column(String())

    def update(self, block):
        link = block.find('div', {'class': 'name'})
        self.event_name = link.get_text().strip()
        self.event_url = link.find('a')["href"]
        self.event_category = Category(block.find('div', {'class': 'category'}).get_text())
        date_children = block.find('div', {'class': 'termin'}).children
        date_string = next(date_children).get_text()
        self.start = datetime.strptime(date_string, "%d.%m.%Y")
        times = next(date_children).get_text().strip()
        check = re.match(r"^([0-9]{1,2}:[0-9]{2}) - ([0-9]{1,2}:[0-9]{2})$", times)
        if check:  # we have a start and end time
            self.start = datetime.combine(self.start.date(), datetime.strptime(check.groups(1)[0], "%H:%M").time())
            self.end = datetime.combine(self.start.date(), datetime.strptime(check.groups(1)[1], "%H:%M").time())
            self.has_time = True
        else:
            check = re.match(r"^([0-9]{1,2}:[0-9]{2})$", times)
            if check:
                self.start = datetime.combine(self.start.date(), datetime.strptime(check.groups(1)[0], "%H:%M").time())
                self.end = datetime.combine(self.start.date(), time(23,59))
                self.has_time = True
            else:
                self.start = datetime.combine(self.start.date(), time(0,0))
                self.end = datetime.combine(self.start.date(), time(23,59))
                self.has_time = False
        group = block.select(".category a")[0]
        self.group_id = group["href"]
        self.excerpt = block.find('div', {'class': 'exerpt'}).get_text()

    def __init__(self, block):
        self.update(block)
        logging.info("Added event "+self.event_name)

    def __str__(self):
        string = "<a href='" + self.event_url + "'><b>" + self.event_name + "</b></a>\n"
        if self.has_time:
            string += "um " + self.start.strftime("%H:%M") + " Uhr "
        if self.group is not None:
            string += "von " + self.group.name
        string += "\n"
        return string

    def is_today(self):
        return self.start.date() <= datetime.today().date() <= self.end.date()