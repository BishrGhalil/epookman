#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb
from sys import argv
import curses

from pookman import Pookman


class Main(object):

    def __init__(self, stdscreen):

        self.screen = stdscreen
        curses.use_default_colors()
        curses.curs_set(0)

        # FIXMEEE: books from deleted directory still exist
        global debug
        if debug:
            pdb.set_trace()

        app = Pookman(self.screen)

        dirs = [
            "/home/bishr/Documents/Books/Novels",
            "/home/bishr/Documents/Books/Programming"
        ]

        app.main()


if __name__ == "__main__":
    global debug
    debug = "-d" in argv or "--debug" in argv

    curses.wrapper(Main)
