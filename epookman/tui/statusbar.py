#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""statusbar class and api"""

from curses import A_BOLD, A_NORMAL

from epookman.core.config import Config
from epookman.tui.ui import UIElement


class StatusBar(UIElement):

    def __init__(self, stdscreen):
        UIElement.__init__(self=self, name="statusbar", stdscreen=stdscreen)
        self.init_window()
        self.set_window_maxyx()

    def init_window(self):
        self.window = self.stdscreen.subwin(self.stdmax_y - Config.padding - 1,
                                            0)
        self.window.keypad(1)

    def print(self, msg, mode=A_NORMAL):
        self.window.clear()
        self.window.addstr(self.max_y - Config.padding, Config.padding, msg,
                           mode)
        self.window.refresh()

    def input(self, msg, mode=A_NORMAL):
        self.window.clear()
        string = UIElement.input(self, msg, mode)
        return string

    def confirm(self, msg, mode=A_BOLD):
        ans = self.input(msg)
        if ans in ["y", "yes"]:
            return True
        else:
            return False
