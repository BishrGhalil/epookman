#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""The Main Class responsible to initialize the EM object and stuff."""

import curses
import pdb
from sys import argv

from epookman.core.epookman import Pookman


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


def main():
    global debug
    debug = "-d" in argv or "--debug" in argv
    curses.wrapper(Main)

