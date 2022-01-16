#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Curses UI Classes and Functions"""

import curses
import logging
from curses import panel
from difflib import get_close_matches

from epookman.core.config import Config
from epookman.data.help import Help


class Menu(object):

    def __init__(self, name, items, stdscreen):
        self.stdscreen = stdscreen
        self.init_window_panel()

        self.name = name

        self.position = 0
        self.items = items
        self.max_y, self.max_x = self.window.getmaxyx()

        self.help = Help(stdscreen)
        self.start_print = 0

    def display(self):
        while True:
            self.window.clear()

            if self.position >= self.max_y - 2:
                self.start_print = self.position - self.max_y + 2
                self.start_print %= len(self.items)
            else:
                self.start_print = 0

            if not self.items:
                self.print_error("Empty", curses.color_pair(5))

            else:
                for index in range(0, len(self.items)):
                    if index == self.max_y - 1:
                        break

                    item = self.items[index + self.start_print]
                    if index + self.start_print == self.position:
                        if item.get("type") != "ebook":
                            mode = curses.color_pair(1)
                        else:
                            mode = curses.color_pair(3)

                    else:
                        if item.get("type") != "ebook":
                            mode = curses.color_pair(2)
                        else:
                            mode = curses.color_pair(4)

                    msg = "%s" % (item["string"])
                    self.window.addstr(Config.padding + index, Config.padding,
                                       msg, mode)

            key = self.window.getch()

            if key in [curses.KEY_ENTER, ord("\n"), ord("l")]:
                if not self.items:
                    self.print_error("Empty", curses.color_pair(5))

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

            elif key == ord("g"):
                key = self.window.getch()
                if key == ord("g"):
                    self.navigate(-self.position)

            elif key == ord("G"):
                self.navigate(len(self.items) - self.position)

            elif key == ord("?"):
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

            elif key == ord("/"):
                string = self.input("Search: ")
                items = [item["string"].lower() for item in self.items]
                match = get_close_matches(string.lower(),
                                          items,
                                          1,
                                          cutoff=0.10)
                if match:
                    index = items.index(match[0])
                    pos = self.position
                    self.navigate(index - pos)

            elif key == ord("a"):
                string = self.input("Directory path: ")
                self.items[0]["take_action"](key="add_dir", name=string)

            elif key == ord("f"):
                item = self.items[self.position]
                item["take_action"](key="toggle_fav", name=item["string"])

            elif key == ord("r"):
                item = self.items[self.position]
                if item.get("type") == "ebook":
                    item["take_action"](key="toggle_mark",
                                        name=item["string"],
                                        value="have_read")
            elif key == ord("t"):
                item = self.items[self.position]
                item["take_action"](key="toggle_mark",
                                    name=item["string"],
                                    value="havent_read")

            elif key == ord("u"):
                item = self.items[self.position]
                item["take_action"](key="scane")

            elif key == ord("c"):
                category = self.input("Category name: ")
                item = self.items[self.position]
                item["take_action"](key="add_category",
                                    name=item["string"],
                                    value=category)

        self.update()

    def input(self, prompt):
        msg = "%s" % prompt
        self.window.addstr(self.max_y - 1, Config.padding, msg,
                           curses.A_NORMAL)
        self.window.refresh()
        string = str()
        while True:
            key = self.window.getch()
            if key in [ord("\n"), curses.KEY_ENTER]:
                return string

            elif key == curses.KEY_BACKSPACE:
                if string:
                    self.window.delch(self.max_y - 1, len(string) + 1)
                    self.window.refresh()
                    string = string[0:-1]
            else:
                string += chr(key)

            msg = "%s%s" % (prompt, string)
            self.window.addstr(self.max_y - 1, Config.padding, msg,
                               curses.A_NORMAL)
            self.window.refresh()

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

    def print_error(self, msg, mode=curses.A_BOLD):
        self.window.addstr(1, Config.padding, msg, mode)

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
        self.stdmax_y, self.stdmax_x = self.stdscreen.getmaxyx()
        self.window = None
        self.init_window()
        self.max_y, self.max_x = self.window.getmaxyx()

    def init_window(self):
        self.window = self.stdscreen.subwin(self.stdmax_y - Config.padding - 1,
                                            0)
        self.window.keypad(1)

    def print(self, msg, mode=curses.A_NORMAL):
        self.window.clear()
        self.window.addstr(self.max_y - Config.padding, Config.padding, msg,
                           mode)
        self.window.refresh()

    def confirm(self, msg, mode=curses.A_BOLD):
        self.window.clear()
        self.window.addstr(self.max_y - Config.padding, Config.padding, msg,
                           mode)
        self.window.refresh()
        key = self.window.getch()
        if key == ord("y"):
            return True

        return False
