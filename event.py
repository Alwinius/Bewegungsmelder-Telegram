#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

from datetime import datetime, time
import re


class Event:
    def __init__(self, block):
        link = block.find('div', {'class': 'name'})
        self.event_name = link.get_text().strip()
        self.event_url = link.find('a')["href"]
        self.event_category = block.find('div', {'class': 'category'}).get_text()
        date_children = block.find('div', {'class': 'termin'}).children
        date_string = next(date_children).get_text()
        self.start = datetime.strptime(date_string, "%d.%m.%Y")
        times = next(date_children).get_text().strip()
        check = re.match(r"^([0-9]{1,2}:[0-9]{2}) - ([0-9]{1,2}:[0-9]{2})$", times)
        if check:  # we have a start and end time
            self.start = datetime.combine(self.start.date(), datetime.strptime(check.groups(1)[0], "%H:%M").time())
            self.end = datetime.combine(self.start.date(), datetime.strptime(check.groups(2)[0], "%H:%M").time())
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
        self.group_link = group["href"]
        self.group_name = group.get_text()
        self.excerpt = block.find('div', {'class': 'exerpt'}).get_text()

    def __str__(self):
        string = "<a href='" + self.event_url + "'><b>" + self.event_name + "</b></a>\n"
        if self.has_time:
            string += "um " + self.start.strftime("%H:%M")\
                 + " Uhr von " + self.group_name + "\n"
        else:
            string += "von " + self.group_name + "\n"
        return string

    def is_today(self):
        return self.start.date() <= datetime.today().date() <= self.end.date()