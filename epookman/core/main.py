#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""The Main Class responsible to initialize the EM object and stuff."""

import curses
import pdb
from sys import argv
import logging

from epookman.core.epookman import Epookman


class Main(object):

    def __init__(self, stdscreen):

        curses.use_default_colors()

        # Color pair for folders and options
        curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
        curses.init_pair(2, curses.COLOR_BLUE, -1)

        # Color pair for ebooks
        curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_GREEN)
        curses.init_pair(4, curses.COLOR_GREEN, -1)

        # for status bar
        curses.init_pair(5, curses.COLOR_RED, -1)

        self.screen = stdscreen
        curses.curs_set(0)

        app = Epookman(self.screen)
        logging.debug("Created Epookman object")

        app.main()


def main():
    if len(argv) > 1:
        if "-h" in argv or "--help" in argv:
            print("Usage: epookman [OPTIONS]\n")
            print("There no options.")
            exit(0)

    curses.wrapper(Main)
