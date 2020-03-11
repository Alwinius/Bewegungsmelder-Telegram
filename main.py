#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# created by Alwin Ebermann (alwin@alwin.net.au)

import sys

from bot import daemon


def usage():
    print("Bewegungsmelder-Telegram-Bot")
    print(f"Usage: {sys.argv[0]} <daemon|notifications>", file=sys.stderr)
    sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
        usage()

    if sys.argv[1] == "daemon":
        daemon.run_daemon()
    elif sys.argv[1] == "notifications":
        print("not implemented")
    elif sys.argv[1] in ("-h", "--help", "help"):
        usage()
    else:
        print("Unknown parameter:", sys.argv[1], file=sys.stderr)
        sys.exit(1)
