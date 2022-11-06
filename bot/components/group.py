#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

from sqlalchemy import Column, String, Integer
from sqlalchemy.orm import relationship

from bot.components.base import Base
from bot.components.event import Event


class Group(Base):
    __tablename__ = 'group'
    url_id = Column(String, unique=True)
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    events = relationship("Event", back_populates="group")

    def __init__(self, url_id: str, name: str):
        self.url_id = url_id
        self.name = name