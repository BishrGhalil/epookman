#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sqlite3
import sys

import magic

from dirent import Dirent

VERSION = "0.1"


class Ebook():

    def __init__(
        self,
        _id=0,
        folder="",
        name="",
        category=None,
        status="fresh",
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


class Pookman():

    def __init__(self):
        self.version = VERSION

        self.db_name = "pookman.db"
        self.db_path = os.path.join(os.getenv("HOME"), self.db_name)

        self.conn = None
        self.cur = None
        self.connect()

        self.create_tables_sql()

        self.dirs = self.fetch_dirs()
        self.ebooks = self.fetch_ebooks()
        self.ebooks_types = "pdf|epub|mobi|azw"  # re pattern

    def __del__(self):
        self.close_connection()

    def addir(self, Dir):
        if isinstance(Dir, Dirent) and Dir not in self.dirs:
            self.dirs.append(Dir)

        else:
            self.error("Not a valid Dirent object")

    def addirs(self, uris):
        if not isinstance(uris, list) and not isinstance(uris, tuple):
            self.error("Not a valid list or tuple")
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

    def fetch_ebooks(self, key="*"):
        res = self.cur.execute(
            "SELECT DISTINCT %s FROM BOOKS ORDER BY FOLDER, NAME, FAV DESC;" %
            key)
        ebooks = []
        if not res:
            return ebooks

        for row in res:
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

    def error(self, msg):
        sys.stderr.write("ERROR: %s\n" % msg)

    def exit_error(self, msg):
        if msg:
            self.error(msg)

        exit(1)

    def main(self):
        print("# books from db")
        ebooks = self.fetch_ebooks()
        for ebook in ebooks:
            print("\t%s" % ebook.name)

        print("# dirs form db")
        dirs = self.fetch_dirs()
        for Dir in dirs:
            print("\t%s" % Dir.path)

        self.close_connection()
