#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Curses UI Classes and Functions"""

import curses
import logging
from curses import panel
from difflib import get_close_matches

from epookman.data.help import Help


class Menu(object):

    def __init__(self, name, items, stdscreen):
        self.stdscreen = stdscreen
        self.init_window_panel()

        self.name = name

        self.position = 0
        self.items = items

        self.help = Help(stdscreen)

    def display(self):
        while True:
            self.window.clear()
            if not self.items:
                self.print_error("Empty")

            else:
                for index, item in enumerate(self.items):
                    if index == self.position:
                        mode = curses.A_REVERSE
                    else:
                        mode = curses.A_NORMAL

                    msg = "%s" % (item["string"])
                    self.window.addstr(1 + index, 1, msg, mode)

            key = self.window.getch()

            if key in [curses.KEY_ENTER, ord("\n"), ord("l")]:
                if not self.items:
                    self.print_error("Empty")

                else:
                    if self.items[self.position].get("args"):
                        args = self.items[self.position]["args"]
                        self.items[self.position]["enter_action"](*args)
                    else:
                        if self.items[self.position]["enter_action"]() == -1:
                            return -1

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
                self.kill()
                return -1
            elif key in [ord("/")]:
                y_value = self.window.getmaxyx()[0]
                msg = "Search: "
                self.window.addstr(y_value - 1, 0, msg, curses.A_NORMAL)
                self.window.refresh()
                string = str()
                while True:
                    key = self.window.getch()
                    if key in [ord('\n'), curses.KEY_ENTER]:
                        items = [item["string"].lower() for item in self.items]
                        match = get_close_matches(string.lower(), items, 5, cutoff=0.10)
                        logging.debug("Matched %s from %s", match, items)

                        if match:
                            index = items.index(match[0])
                            nav = index - self.position 
                            self.navigate(nav)
                        break

                    elif key in [curses.KEY_BACKSPACE]:
                        if string:
                            self.window.delch(y_value - 1, len(string) + 1)
                            string = string.replace(string[-1], "")

                    else:
                        string += chr(key)

                    msg = "Search: %s" % string
                    self.window.addstr(y_value - 1, 0, msg,
                                       curses.A_NORMAL)
                    self.window.refresh()

        self.update()

    def init_window_panel(self):
        self.window = self.stdscreen.subwin(0, 0)
        self.window.keypad(1)
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= len(self.items):
            self.position = len(self.items) - 1

    def print_error(self, msg):
        mode = curses.A_BOLD
        self.window.addstr(1, 1, msg, mode)

    def update(self):
        self.window.clear()
        self.panel.hide()
        panel.update_panels()
        self.panel.top()
        self.panel.show()

    def kill(self):
        self.window.erase()


class StatusBar(object):

    def __init__(self, stdscreen):
        self.stdscreen = stdscreen
        self.window = None
        self.init_window()

    def init_window(self):
        y_value, x_value = self.stdscreen.getmaxyx()
        self.window = self.stdscreen.subwin(y_value - 1, 0)
        self.window.keypad(1)

    def print(self, msg, mode=curses.A_NORMAL):
        self.window.clear()
        self.window.addstr(0, 0, msg, mode)
        self.window.refresh()

    def confirm(self, msg, mode=curses.A_BOLD):
        self.window.clear()
        self.window.addstr(0, 0, msg, mode)
        self.window.refresh()
        key = self.window.getch()
        if key in [ord('y')]:
            return True

        return False
