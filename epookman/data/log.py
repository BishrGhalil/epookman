#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""logging configuration for epookman"""

import logging

logging.basicConfig(filename='epookman.log',
                    level=logging.DEBUG,
                    format="%(asctime)s:%(levelname)s:%(message)s")
