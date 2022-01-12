#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Curses Menus Classes and Functions"""

import curses
import logging
from curses import panel

from epookman.data.help import Help


class Menu(object):

    def __init__(self, name, items, stdscreen):
        self.window = stdscreen.subwin(0, 0)
        self.window.keypad(1)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()

        self.name = name

        self.position = 0
        self.items = items

        self.help = Help(stdscreen)

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1

    def print_error(self, msg):
        mode = curses.A_BOLD
        self.window.addstr(1, 1, msg, mode)

    def display(self):
        self.panel.top()
        self.panel.show()
        self.window.clear()

        while True:

            x_value, y_value = self.window.getmaxyx()
            logging.debug("Got max_x %s and max_y %s", x_value, y_value)
            msg = "Press ? to show help"
            mode = curses.A_NORMAL
            self.window.addstr(x_value - 1, 0, msg, mode)


            self.window.refresh()
            curses.doupdate()
            if not self.items:
                self.print_error("Empty")

            else:
                for index, item in enumerate(self.items):
                    if index == self.position:
                        mode = curses.A_REVERSE
                    else:
                        mode = curses.A_NORMAL

                    msg = "%s" % (item[0])
                    self.window.addstr(1 + index, 1, msg, mode)

            key = self.window.getch()

            if key in [curses.KEY_ENTER, ord("\n"), ord("l")]:
                if not self.items:
                    self.print_error("Empty")

                else:
                    self.items[self.position][1]()

            elif key in [curses.KEY_UP, ord("k")]:
                self.navigate(-1)

            elif key in [curses.KEY_DOWN, ord("j")]:
                self.navigate(1)

            elif key in [ord("?")]:
                self.help.display()

            elif key in [curses.KEY_LEFT, ord("h")]:
                if self.name != "main":
                    break
            elif key in [
                    ord("q"), curses.KEY_EXIT, curses.KEY_CLOSE,
                    curses.KEY_CANCEL
            ]:
                break

        self.window.clear()
        self.panel.hide()
        panel.update_panels()
