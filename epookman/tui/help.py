#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Curses Help Classe for epookman"""


class Help(object):

    def __init__(self, stdscreen):
        x_value = 1
        y_value = 0
        self.window = stdscreen.subwin(x_value, y_value)

        self.keybinds = [
            ["h", "Move left"],
            ["j", "Move down"],
            ["k", "Move up"],
            ["l", "Move right"],
            ["gg", "Top of page"],
            ["G", "End of page"],
            ["a", "Add a directory"],
            ["f", "Toggle (add to favorite)"],
            ["r", "mark as 'have read'"],
            ["t", "mark as 'haven't read'"],
            ["u", "Update database (scane)"],
            ["q", "Quite"],
            ["/", "Search"],
            ["?", "Show help"],
        ]

    def display(self):
        self.window.clear()

        msg = "KEY\tHelp"
        self.window.addstr(0, 1, msg)

        for index, keybind in enumerate(self.keybinds):
            key = keybind[0]
            key_help = keybind[1]
            msg = "%s\t%s" % (key, key_help)
            self.window.addstr(1 + index, 1, msg)

        self.window.refresh()

        key = self.window.getkey()
        self.window.clear()
        self.window.refresh()
