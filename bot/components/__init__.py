#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

import configparser
from pathlib import Path

BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent
CONFIG_FILE = str(BASE_DIR / "config.ini")
DB_FILE = str(BASE_DIR / "bewegungsmelder.sqlite")

_parser = configparser.ConfigParser()
_parser.read(CONFIG_FILE)
config = _parser['DEFAULT']
