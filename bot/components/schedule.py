#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

import enum


class Schedule(enum.Enum):
    NONE = "k"
    WEEKLY = "wöchentlich "
    DAILY = "täglich "
