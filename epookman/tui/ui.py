#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Curses UI Classes and Functions"""
from curses import A_NORMAL, KEY_ENTER, KEY_BACKSPACE


class UIElement(object):

    def __init__(self, name, stdscreen):
        self.stdscreen = stdscreen
        self.stdmax_y, self.stdmax_x = self.stdscreen.getmaxyx()

        self.name = name
        self.window = None

    def display(self):
        """Override this"""

    def input(self, prompt, mode=A_NORMAL):
        msg = "%s" % prompt

        self.window.addstr(self.max_y - 1, Config.padding, msg, mode)

        self.window.refresh()
        string = str()

        while True:
            key = self.window.getch()
            if key in [ord("\n"), KEY_ENTER]:
                return string

            elif key == KEY_BACKSPACE:
                if string:
                    self.window.delch(self.max_y - 1, len(string) + 1)
                    self.window.refresh()
                    string = string[0:-1]
            else:
                string += chr(key)

            msg = "%s%s" % (prompt, string)
            self.window.addstr(self.max_y - 1, Config.padding, msg, mode)
            self.window.refresh()

    def init_window(self):
        """Override this"""

    def set_window_maxyx(self):
        self.max_y, self.max_x = self.window.getmaxyx()

    def update(self):
        """Override this"""

    def kill(self):
        self.window.erase()
