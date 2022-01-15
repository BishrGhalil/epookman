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
from epookman.api.dirent import check_path


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
                self.print_error("Empty", curses.color_pair(5))

            else:
                for index, item in enumerate(self.items):
                    if index == self.position:
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
                    self.window.addstr(1 + index, 1, msg, mode)

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
                if not check_path(string):
                    string = self.items[0]["take_action"](
                        key="print_status", name="Not a valid path")

                else:
                    self.items[0]["take_action"](key="add_dir", name=string)

            elif key == ord("f"):
                item = self.items[self.position]
                item["take_action"](key="toggle_fav", name=item["string"])

            elif key == ord("m"):
                item = self.items[self.position]
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
        y_value = self.window.getmaxyx()[0]
        msg = "%s" % prompt
        self.window.addstr(y_value - 1, 0, msg, curses.A_NORMAL)
        self.window.refresh()
        string = str()
        while True:
            key = self.window.getch()
            if key in [ord("\n"), curses.KEY_ENTER]:
                return string

            elif key == curses.KEY_BACKSPACE:
                if string:
                    self.window.delch(y_value - 1, len(string) + 1)
                    self.window.refresh()
                    string = string[0:-1]
            else:
                string += chr(key)

            msg = "%s%s" % (prompt, string)
            self.window.addstr(y_value - 1, 0, msg, curses.A_NORMAL)
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
