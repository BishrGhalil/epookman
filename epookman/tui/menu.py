#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Menu class and api"""

import curses
import logging
from curses import panel
from difflib import get_close_matches

from epookman.api.ebook import Ebook
from epookman.core.config import Config, Key
from epookman.tui.help import Help
from epookman.tui.ui import UIElement


class Menu(UIElement):

    def __init__(self, name, items, stdscreen):
        UIElement.__init__(self=self, name=name, stdscreen=stdscreen)
        self.init_window()
        self.init_panel()
        self.set_window_maxyx()

        self.items = items
        self.items_len = len(self.items)

        self.position = 0
        self.start_print = 0

        self.help = Help(stdscreen)

    def check_scrolling(self):

        if self.position >= self.max_y - 3:
            self.start_print = self.position - self.max_y + 3
            self.start_print %= self.items_len
        else:
            self.start_print = 0

    def get_print_mode(self, item, highligh=False):
        if item.get("type") != "ebook":
            if highligh:
                mode = curses.color_pair(1)
            else:
                mode = curses.color_pair(2)

        else:
            if highligh:
                mode = curses.color_pair(3)
            else:
                mode = curses.color_pair(4)

        return mode

    def display(self):

        while True:
            self.window.clear()
            self.check_scrolling()

            if not self.items:
                self.print_error("Empty", curses.color_pair(5))

            else:
                for index in range(0, self.items_len):
                    if index == self.max_y - 2:
                        break

                    item = self.items[index + self.start_print]

                    if index + self.start_print == self.position:
                        mode = self.get_print_mode(item, highligh=True)

                    else:
                        mode = self.get_print_mode(item)

                    msg = "%s" % (item["string"])
                    self.window.addstr(Config.padding + index, Config.padding,
                                       msg, mode)

            key = self.window.getch()

            # status: 0 == break, -1 == return
            status = self.handle_keypress(key)
            if status == 0:
                break
            elif status == -1:
                return -1

        self.update()

    def handle_keypress(self, key):

        if key in Key.KEY_ENTER:

            if not self.items:
                return 1

            if self.items[self.position].get("args"):
                args = self.items[self.position]["args"]
                self.items[self.position]["enter_action"](*args)

            else:
                if self.items[self.position]["enter_action"]() == -1:
                    return -1

        elif key in Key.KEY_UP:
            self.navigate(-1)

        elif key in Key.KEY_DOWN:
            self.navigate(1)

        elif key in Key.KEY_LEFT:
            if self.name != "main":
                return 0

        elif key in Key.KEY_MOVE_TOP:
            key = self.window.getch()
            if key in Key.KEY_MOVE_TOP:
                self.navigate(-self.position)

        elif key in Key.KEY_MOVE_END:
            self.navigate(self.items_len - self.position)

        elif key in Key.KEY_HELP:
            self.help.display()

        elif key in Key.KEY_QUITE:
            self.kill()
            return -1

        elif key in Key.KEY_SEARCH:
            query = self.input("Search: ")
            if query:
                self.search_navigate(query)

        elif key in Key.KEY_ADD:
            string = self.input("Directory path: ")
            if not string:
                return 1
            self.items[0]["take_action"](key="add_dir", name=string)

        elif key in Key.KEY_FAV:
            item = self.items[self.position]
            if item.get("type") != "ebook":
                return 1
            item["take_action"](key="toggle_fav", name=item["string"])

        elif key in Key.KEY_HAVE_READ:
            item = self.items[self.position]
            if item.get("type") == "ebook":
                item["take_action"](key="toggle_mark",
                                    name=item["string"],
                                    value=Ebook.STATUS_HAVE_READ)
        elif key in Key.KEY_HAVE_NOT_READ:
            item = self.items[self.position]
            if item.get("type") != "ebook":
                return 1
            item["take_action"](key="toggle_mark",
                                name=item["string"],
                                value=Ebook.STATUS_HAVE_NOT_READ)

        elif key in Key.KEY_SCANE:
            item = self.items[self.position]
            item["take_action"](key="scane")

        elif key in Key.KEY_ADD_CATEGORY:
            category = self.input("Category name: ")
            item = self.items[self.position]
            if item.get("type") != "ebook":
                return 1
            item["take_action"](key="add_category",
                                name=item["string"],
                                value=category)

    def init_window(self):
        self.window = self.stdscreen.subwin(0, 0)
        self.window.keypad(1)

    def init_panel(self):
        self.panel = panel.new_panel(self.window)
        self.panel.hide()
        panel.update_panels()

    def navigate(self, n):
        self.position += n
        if self.position < 0:
            self.position = 0
        elif self.position >= self.items_len:
            self.position = self.items_len - 1

    def search(self, query):
        query = query.lower()
        items = [item["string"].lower() for item in self.items]
        for item in items:
            if item.startswith(query):
                query = item

        match = get_close_matches(query, items, 1, cutoff=0.10)

        if match:
            match = match[0]
            index = items.index(match)
            return match, index

        else:
            return None, None

    def search_navigate(self, query):
        match, index = self.search(query)

        if match:
            pos = self.position
            self.navigate(index - pos)

    def print_error(self, msg, mode=curses.A_BOLD):
        self.window.addstr(1, Config.padding, msg, mode)

    def update(self):
        self.window.clear()
        self.panel.hide()
        panel.update_panels()
        self.panel.top()
        self.panel.show()
