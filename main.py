#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

import sys

from bot import daemon


def usage():
    print("Bewegungsmelder-Telegram-Bot")
    print(f"Usage: {sys.argv[0]} <daemon|scrape>", file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()

    if sys.argv[1] == "daemon":
        daemon.run_daemon()
    elif sys.argv[1] == "scrape":
        daemon.scraper_callback()
    elif sys.argv[1] == "weekly":
        daemon.send_weekly_notifications()
    elif sys.argv[1] in ("-h", "--help", "help"):
        usage()
    else:
        print("Unknown parameter:", sys.argv[1], file=sys.stderr)
        sys.exit(1)
