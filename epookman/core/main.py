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

        self.screen = stdscreen
        curses.use_default_colors()
        curses.curs_set(0)

        app = Epookman(self.screen)
        logging.debug("Created Epookman object")

        logging.debug("Scaned dirs")
        app.main()


def main():
    if len(argv) > 1:
        if "-h" in argv or "--help" in argv:
            print("Usage: epookman [OPTIONS]\n")
            print("There no options.")
            exit(0)

    try:
        curses.wrapper(Main)
    except Exception as e:
        logging.error(e)
        exit(1)
