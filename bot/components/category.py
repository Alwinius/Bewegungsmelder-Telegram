#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

import enum


class Category(str, enum.Enum):
    AKTION = "Aktion"
    DEMO = "Demonstration & Kundgebung"
    DISKUSSION = "Diskussion"
    ESSEN = "Essen, Trinken & Kochen"
    VORTRAG = "Vortrag & Infoveranstaltung"
    BERATUNG = "Beratung"
    LESUNG = "Lesung & Buchvorstellung"
    KUNST = "Kunst, Kultur, Theater & Film"
    MARKT = "Markt & zu verschenken"
    MUSIK = "Musik, Konzert & Party"
    PLENUM = "Plenum & regelm.Treffen"
    GERICHT = "Gerichtsprozess"
    OUTDOOR = "Rundgang & Outdoor"
    WORKSHOP = "Workshop & Skillssharing"
    SONSTIGES = "Sonstiges"




