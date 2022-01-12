#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os

VERSION = "0.1"


class Dirent():

    def __init__(self, uri=""):
        self.version = VERSION
        self.path = uri
        self.files = []
        self.ents = []
        self.recurs = 1

    def toggle_recurs():
        self.recurs = not self.recurs

    def getfiles_from_path(self, path):
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
