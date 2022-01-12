#!/usr/bin/env python
# -*- coding: utf-8 -*-

import curses
import os
import re
import sqlite3
import sys
from curses import panel

import magic

from curses_menus import *
from dirent import Dirent

VERSION = "0.1"
ebook_reader = "zathura"


def pm_error(msg):
    sys.stderr.write("ERROR: %s\n" % msg)


def pm_exit_error(msg):
    if msg:
        pm_error(msg)

    exit(1)


class Ebook():

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

    def toggle_status(self):
        self.status = not self.status

    def open_ebook(self):
        uri = os.path.join(self.folder, self.name)
        global ebook_reader

        cmd = "%s \"%s\" > /dev/null 2>&1" % (ebook_reader, uri)
        if not os.system(cmd):
            msg = "Couldn't open %s" % uri
            pm_error(msg)


class Pookman(object):

    def __init__(self, stdscreen):
        self.version = VERSION

        self.db_name = "pookman.db"
        self.db_path = os.path.join(os.getenv("HOME"), self.db_name)

        self.conn = None
        self.cur = None
        self.connect()

        self.create_tables_sql()

        self.dirs = self.fetch_dirs()
        self.ebooks = self.fetch_ebooks()

        # re pattern for supported ebooks types
        self.ebooks_types = "pdf|epub|mobi|azw"

        self.main_menu = None
        self.screen = stdscreen
        self.make_menus()

    def __del__(self):
        self.close_connection()

    def addir(self, Dir):
        if isinstance(Dir, Dirent) and Dir not in self.dirs:
            self.dirs.append(Dir)

        else:
            pm_error("Not a valid Dirent object")

    def addirs(self, uris):
        if not isinstance(uris, list) and not isinstance(uris, tuple):
            pm_error("Not a valid list or tuple")
        else:
            for uri in uris:
                Dir = Dirent(uri)
                self.addir(Dir)

            self.commit_dirs_sql()

    def close_connection(self):
        if self.conn:
            self.conn.close()

        self.conn = None

    def create_tables_sql(self):
        self.cur.execute(
                "CREATE TABLE IF NOT EXISTS DIRS(" \
                "ID INTEGER PRIMARY KEY AUTOINCREMENT," \
                "PATH           TEXT NOT NULL," \
                "RECURS         INT NOT NULL);"
        )

        self.cur.execute(
                "CREATE TABLE IF NOT EXISTS BOOKS(" \
                "ID INTEGER PRIMARY KEY AUTOINCREMENT," \
                "FOLDER         TEXT    NOT NULL," \
                "NAME           TEXT    NOT NULL," \
                "CATEGORY       TEXT," \
                "STATUS         INT," \
                "FAV            INT);")

        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_fav ON BOOKS (FAV);")

        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_category ON BOOKS (CATEGORY);")
        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_status ON BOOKS (STATUS);")

        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_folder ON BOOKS (FOLDER);")

        self.conn.commit()

    def connect(self):
        self.conn = sqlite3.connect(self.db_path)
        self.cur = self.conn.cursor()
        return self.conn

    def commit_dirs_sql(self):
        for Dir in self.dirs:
            data = (Dir.path, Dir.path, Dir.recurs)
            self.cur.execute(
                "INSERT OR REPLACE INTO DIRS (ID, PATH, RECURS) \
                              VALUES ((SELECT ID FROM DIRS WHERE PATH = ?), ?, ?);",
                data)

        self.conn.commit()

    def commit_ebooks_sql(self):
        for ebook in self.ebooks:
            data = (ebook.name, ebook.folder, ebook.name, ebook.category,
                    ebook.status, ebook.fav)
            self.cur.execute(
                "INSERT OR REPLACE INTO BOOKS (ID, FOLDER, NAME, " \
                "CATEGORY, STATUS, FAV) " \
                "VALUES ((SELECT ID FROM BOOKS WHERE NAME = ?), ?, ?, ?, ?, ?);",
            data)

        self.conn.commit()

    def del_dir(self, path):
        res = self.cur.execute("DELETE FROM DIRS WHERE PATH=?;", (path, ))
        self.conn.commit()
        self.dirs = self.fetch_dirs()

    def fetch_ebooks(self, key="*", where=None, sort_clause=None):
        if not sort_clause:
            sort_clause = "ORDER BY NAME, FAV DESC"

        if not where:
            res = self.cur.execute("SELECT DISTINCT %s FROM BOOKS %s;" %
                                   (key, sort_clause))
        else:
            res = self.cur.execute(
                "SELECT DISTINCT %s FROM BOOKS WHERE %s %s;" %
                (key, where, sort_clause))

        ebooks = []
        if not res:
            return ebooks

        for row in res:
            if len(row) == 1:
                ebooks.append(row[0])
            else:
                ebook = Ebook(folder=row[1],
                              name=row[2],
                              category=row[3],
                              status=row[4],
                              fav=row[5])
                ebooks.append(ebook)

        return ebooks

    def fetch_dirs(self):
        res = self.cur.execute("SELECT DISTINCT * FROM DIRS ORDER BY PATH;")
        dirs = []

        if not res:
            return dirs

        for row in res:
            Dir = Dirent()
            Dir.set_values(row[1], row[2])
            dirs.append(Dir)

        return dirs

    def make_menus(self):
        # reding menu
        reading_menu_items = [(ebook.name, ebook.open_ebook)
                              for ebook in self.fetch_ebooks(where="status=1")]
        reading_menu = Menu("reading", reading_menu_items, self.screen)

        # have read menu
        have_read_menu_items = [
            (ebook.name, ebook.open_ebook)
            for ebook in self.fetch_ebooks(where="status=2")
        ]
        have_read_menu = Menu("have_read", have_read_menu_items, self.screen)

        # haven't read menu
        havent_read_menu_items = [
            (ebook.name, ebook.open_ebook)
            for ebook in self.fetch_ebooks(where="status=0")
        ]
        havent_read_menu = Menu("havent_read", havent_read_menu_items,
                                self.screen)

        # all menu
        all_menu_items = [(ebook.name, ebook.open_ebook)
                          for ebook in self.fetch_ebooks()]
        all_menu = Menu("all", all_menu_items, self.screen)

        # folders menu
        folders_menu_items = []
        for Dir in self.dirs:
            dir_ebooks = [
                ebook for ebook in self.fetch_ebooks(
                    where=f"folder like \'{Dir.path}%\'")
            ]
            dir_menu_items = [(ebook.name, ebook.open_ebook)
                              for ebook in dir_ebooks]
            dir_menu = Menu(Dir.path, dir_menu_items, self.screen)
            folders_menu_items.append((Dir.path, dir_menu.display))

        folders_menu = Menu("folders", folders_menu_items, self.screen)

        # categories menu
        categories_menu_items = []
        categories_list = self.fetch_ebooks(key="category")
        for cat in categories_list:
            cat_ebooks = [
                ebook
                for ebook in self.fetch_ebooks(where="category=\'%s\'" % cat)
            ]
            cat_menu_items = [(ebook.name, ebook.open_ebook)
                              for ebook in cat_ebooks]
            cat_menu = Menu(cat, cat_menu_items, self.screen)
            categories_menu_items.append((cat, cat_menu.display))

        categories_menu = Menu("categories", categories_menu_items,
                               self.screen)

        # favorites menu
        favorites_menu_items = [(ebook.name, ebook.open_ebook)
                                for ebook in self.fetch_ebooks(where="fav=1")]
        favorites_menu = Menu("favorites", favorites_menu_items, self.screen)

        main_menu_items = [
            ("Reading", reading_menu.display),
            ("Folders", folders_menu.display),
            ("Favorites", favorites_menu.display),
            ("Categories", categories_menu.display),
            ("Have read", have_read_menu.display),
            ("Haven't read", havent_read_menu.display),
            ("All", all_menu.display),
        ]

        self.main_menu = Menu("main", main_menu_items, self.screen)

    def scane(self):
        res = self.cur.execute("DELETE FROM BOOKS;")
        self.conn.commit()

        mime = magic.open(magic.MAGIC_MIME)
        mime.load()

        for Dir in self.dirs:
            Dir.getfiles()
            for file in Dir.files:
                mime_type = mime.file(file)
                if re.search(self.ebooks_types, mime_type):
                    ebook = Ebook()
                    ebook.set_path(file)
                    self.ebooks.append(ebook)

        self.update_db()

    def update_db(self):
        self.commit_dirs_sql()
        self.commit_ebooks_sql()

    def main(self):
        self.main_menu.display()
        self.close_connection()
