#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

import requests
from bs4 import BeautifulSoup
from bot.components.base import Session
from bot.components.event import Event
from bot.components.group import Group


class Scraper:
    SCRAPE_PAGES: int = 5

    @staticmethod
    def get_events_block(page_id: int):
        payload = "event-atts%5B%5D=Aktion&event-atts%5B%5D=Demonstration+%26+Kundgebung&event-atts%5B%5D=Diskussion" \
                  "&event-atts%5B%5D=Essen%2C+Trinken+%26+Kochen&event-atts%5B%5D=Kunst%2C+Kultur%2C+Theater+%26+Film" \
                  "&event-atts%5B%5D=Lesung+%26+Buchvorstellung&event-atts%5B%5D=Markt+%26+zu+verschenken&event-atts%5B" \
                  "%5D=Musik%2C+Konzert+%26+Party&event-atts%5B%5D=Plenum+%26+regelm.Treffen&event-atts%5B%5D" \
                  "=Gerichtsprozess&event-atts%5B%5D=Rundgang+%26+Outdoor&event-atts%5B%5D=Sonstiges&event-atts%5B%5D" \
                  "=Vortrag+%26+Infoveranstaltung&event-atts%5B%5D=Workshop+%26+Skillssharing&event-atts%5B%5D=Beratung" \
                  "&submit=Ausw%C3%A4hlen"
        page = requests.post("https://bewegungsmelder-aachen.de/kalender/?pno=" + str(page_id), data=payload,
                             headers={'Content-Type': 'application/x-www-form-urlencoded'})
        soup = BeautifulSoup(page.content, "lxml")
        return soup.select(".post-column")

    @staticmethod
    def prepare_event_info(block):
        link = block.find('div', {'class': 'name'})
        event_url = link.find('a')["href"]
        group = block.select(".category a")[0]
        group_link = group["href"]
        group_name = group.get_text()
        return [event_url, group_name, group_link]

    @staticmethod
    def start_scraping():
        session: Session = Session()

        for i in range(Scraper.SCRAPE_PAGES):  # extend here
            events_block = Scraper.get_events_block(i)
            for event_block in events_block:
                e = Scraper.prepare_event_info(event_block)
                stored_event: Event = session.query(Event).filter(Event.event_url == e[0]).first()
                if stored_event is None:
                    # check if group exists before creating event
                    stored_group = session.query(Group).filter(Group.url_id == e[2]).first()
                    if stored_group is None:
                        g = Group(url_id=e[2], name=e[1])
                        session.add(g)
                        session.commit()
                    new_event = Event(event_block)
                    session.add(new_event)
                    session.commit()
                else:
                    stored_event.update(event_block)
                    session.commit()
        session.close()
