#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from . import DB_FILE

engine = create_engine('sqlite:///' + DB_FILE)
Session = sessionmaker(bind=engine)

Base = declarative_base()
Base.metadata.create_all(engine)