#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Curses Screen for ebook meta data"""

from epookman.tui.ui import UIElement
from epookman.core.config import Config


class EbookMetaData(UIElement):

    def __init__(self, stdscreen):
        UIElement.__init__(self=self, name="help", stdscreen=stdscreen)
        self.init_window()

    def display(self, ebook):
        self.window.clear()

        msg = "Meta Data:"
        self.window.addstr(0, 1, msg)

        data = ebook.get_data()
        metadata = ebook.get_meta_data()
        data.update(metadata)

        for index, key in enumerate(data.keys()):
            msg = "%-10s\t%s" % (key, data.get(key))
            self.window.addstr(1 + index, 1, msg)

        self.window.refresh()

        key = self.window.getkey()
        self.window.clear()
        self.window.refresh()

    def init_window(self):
        y_value = 0
        x_value = 0
        self.window = self.stdscreen.subwin(Config.padding + y_value,
                                            Config.padding + x_value)
