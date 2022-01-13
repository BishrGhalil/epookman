#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""File system scraper"""

import logging
import os
from sys import stderr


class Dirent():

    def __init__(self, uri=""):

        self.check_path(uri)
        self.path = uri
        self.files = []
        self.ents = []
        self.recurs = 1

    def check_path(self, path):
        logging.debug("Checking path on %s", path)
        if not os.path.lexists(path):
            logging.error("Not a valid directory path %s", path)

    def toggle_recurs():
        self.recurs = not self.recurs

    def getfiles_from_path(self, path):
        self.check_path(path)
        ents = os.scandir(path)

        for ent in ents:
            if os.path.isdir(ent.path):
                if self.recurs:
                    self.getfiles_from_path(ent.path)
                else:
                    continue

            else:
                self.ents.append(ent)
                self.files.append(ent.path)

    def getfiles(self):
        path = self.path
        self.getfiles_from_path(path)

    def set_values(self, uri, recurs):
        self.path = uri
        self.recurs = recurs

    def __str__(self):
        return self.path