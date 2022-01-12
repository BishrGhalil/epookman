#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Check file mime type"""

import re

import magic

T_EBOOK = 0


class Mime():

    def __init__(self):
        self.mime = magic.open(magic.MAGIC_MIME)
        self.mime.load()
        self.re_ebooks_types = "pdf|epub|mobi|azw"


    def mime_type(self, file):
        mime_t = self.mime.file(file)
        if re.search(self.re_ebooks_types, mime_t):
            return T_EBOOK
