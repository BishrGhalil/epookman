#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pdb
from pookman import *

if __name__ == "__main__":
    dirs = [
        "/home/bishr/Documents/Books/Linux",
        "/home/bishr/Documents/Books/Novels"
    ]

    #  pdb.set_trace()
    app = Pookman()
    app.addirs(dirs)
    # FIXMEEE: books from deleted directory still exist
    app.del_dir("/home/bishr/Documents/Books/Novels")
    app.scane()
    app.main()
