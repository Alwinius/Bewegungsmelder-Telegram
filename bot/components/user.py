#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

from sqlalchemy import Column, Integer, String, Table, ForeignKey, Enum
from sqlalchemy.orm import relationship
from bot.components.base import Base
from bot.components.array_of_enum import ArrayOfEnum
from bot.components.category import Category
from bot.components.schedule import Schedule
from bot.components.group import Group

association_table = Table('association', Base.metadata,
                          Column('user_id', Integer, ForeignKey('user.id')),
                          Column('group_id', Integer, ForeignKey('group.url_id'))
                          )


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    title = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    counter = Column(Integer(), nullable=True)
    notify_schedule = Column(Enum(Schedule))
    excluded_groups = relationship("Group", secondary=association_table)
    selected_categories = Column(ArrayOfEnum())
    message_id = Column(Integer(), nullable=True)

    def __init__(self, id, first_name, last_name, username, title):
        self.id = id
        self.first_name = first_name
        self.last_name = last_name
        self.username = username
        self.notify_schedule = Schedule.DAILY
        self.selected_categories = [e for e in Category]
        self.title = title
        self.counter = 0
