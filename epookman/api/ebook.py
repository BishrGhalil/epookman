#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Ebook functions and consts"""

import os


class Ebook():

    STATUS_HAVE_NOT_READ = 0
    STATUS_READING = 1
    STATUS_HAVE_READ = 2

    def __init__(
        self,
        _id=0,
        folder="",
        name="",
        category=None,
        status=0,
        fav=0,
    ):

        self.name = name
        self.id = _id
        self.folder = folder
        self.category = category
        self.status = status
        self.fav = fav

    def set_path(self, path):
        self.folder = os.path.dirname(path)
        self.name = os.path.basename(path)

    def toggle_fav(self):
        self.fav = not self.fav

    def set_status(self, status):
        self.status = status

    def set_category(self, category):
        self.category = category

    def get_path(self):
        uri = os.path.join(self.folder, self.name)
        return uri

    @classmethod
    def get_status_string(cls, status):
        if status == cls.STATUS_HAVE_NOT_READ:
            return "Have not read"
        elif status == cls.STATUS_HAVE_READ:
            return "Have read"
        elif status == cls.STATUS_READING:
            return "Reading"
