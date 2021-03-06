#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Ebook functions and consts"""

import os

import epub_meta
import PyPDF2
from PyPDF2 import PdfFileReader

EBOOK_TYPE_PDF = 0
EBOOK_TYPE_EPUB = 1
EBOOK_TYPE_MOBI = 2
EBOOK_TYPE_XPS = 3
EBOOK_TYPE_CBR = 4
EBOOK_TYPE_CBZ = 5


class Ebook():
    STATUS_HAVE_NOT_READ = 0
    STATUS_READING = 1
    STATUS_HAVE_READ = 2

    def __init__(self,
                 _id=0,
                 folder="",
                 name="",
                 category=None,
                 status=0,
                 fav=0,
                 ebook_type=None):

        self.name = name
        self.id = _id
        self.folder = folder
        self.category = category
        self.status = status
        self.fav = fav
        self.type = ebook_type

        self.ebook_types = {
            "pdf": EBOOK_TYPE_PDF,
            "epub": EBOOK_TYPE_EPUB,
            "mobi": EBOOK_TYPE_MOBI,
            "xps": EBOOK_TYPE_XPS,
            "cbr": EBOOK_TYPE_CBR,
            "cbz": EBOOK_TYPE_CBZ
        }

    def set_path(self, path):
        self.folder = os.path.dirname(path)
        self.name = os.path.basename(path)

    def toggle_fav(self):
        self.fav = not self.fav

    def set_status(self, status):
        self.status = status

    def set_category(self, category):
        self.category = category

    def set_type(self, ebook_type):
        self.type = ebook_type

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

    def get_type_string(self):
        for ebook_type in self.ebook_types.keys():
            if self.type == self.ebook_types.get(ebook_type):
                return ebook_type

    def get_fav_string(self):
        if self.fav:
            return "True"
        else:
            return "False"

    def get_data(self):
        data = {
            "name": self.name,
            "folder": self.folder,
            "type": self.get_type_string(),
            "category": self.category,
            "fav": self.get_fav_string(),
            "status": self.get_status_string(self.status),
        }

        return data

    def get_meta_data(self):
        data = dict()

        path = self.get_path()
        size = os.stat(path)
        size = "%.2f" % (size.st_size / (1024**2))
        data["File Size"] = size
        if self.type == EBOOK_TYPE_PDF:
            with open(path, "rb") as file:
                pdfreader = PdfFileReader(file)
                data["Encrypt"] = pdfreader.isEncrypted
                if not data.get("Encrypt"):
                    data["Number of Pages"] = pdfreader.numPages
                    info = pdfreader.documentInfo
                    data["Creation Date"] = info.get('/CreationDate')
                    data["Modification Date"] = info.get('/ModDate')
                    data["Creators"] = info.get('/Creator')

        if self.type == EBOOK_TYPE_EPUB:
            tmp_data = epub_meta.get_epub_metadata(path,
                                                   read_cover_image=False,
                                                   read_toc=False)
            data["Creators"] = tmp_data.authors
            data["Creation Date"] = tmp_data.publication_date

        return data
