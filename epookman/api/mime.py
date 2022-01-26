#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Check file mime type"""

import re

import magic

MIME_TYPE_EBOOK_PDF = 0
MIME_TYPE_EBOOK_EPUB = 1
MIME_TYPE_EBOOK_MOBI = 2
MIME_TYPE_EBOOK_XPS = 3
MIME_TYPE_EBOOK_CBR = 4
MIME_TYPE_EBOOK_CBZ = 5


class Mime():

    def __init__(self):
        self.mime = magic.open(magic.MAGIC_MIME)
        self.mime.load()

    def mime_type(self, file):
        mime_t = self.mime.file(file)
        return mime_t

    def is_ebook(self, mime_type):
        ebooks_pattern = "application/(pdf|epub|mobi|xps|cbr|cbz); .*"
        if re.search(ebooks_pattern, mime_type):
            return True
        else:
            return False
