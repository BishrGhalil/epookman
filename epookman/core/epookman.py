#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.

# TODOO: Threads, for scane
# TODOO: Configuration file
# TODOOO: print ebook details and meta data
# TODO: tests
# FIXMEE: ebooks from sub dirs are deleted when deleting main dirs
# FIXMEEE: Cleaner Code

import curses
import logging
import os
import re
import sqlite3
import sys
from time import sleep

import magic

from epookman.api.dirent import Dirent, check_path
from epookman.api.mime import MIME_TYPE_EBOOK, Mime
from epookman.api.ebook import Ebook
from epookman.core.config import Config
from epookman.tui.menu import Menu
from epookman.tui.statusbar import StatusBar


class Epookman(object):

    def __init__(self, stdscreen):
        self.db_name = "pookman.db"
        self.db_path = os.path.join(os.getenv("HOME"), self.db_name)
        logging.debug("Initialized db name to %s and db path to %s",
                      self.db_name, self.db_path)

        self.conn = None
        self.cur = None

        self.connect()
        logging.debug("Made connection to the database")

        self.create_tables_sql()
        logging.debug("Tables created")

        self.dirs = self.fetch_dirs()
        logging.debug("Fetched dirs from database")
        self.ebooks = self.fetch_ebooks()
        logging.debug("Fetched ebooks from database")
        self.ebooks_files = self.ebooks_files_init()
        logging.debug("Making ebooks_files list from ebooks list")

        self.main_menu = None
        self.screen = stdscreen

        y_val = self.screen.getmaxyx()[0]
        self.menu_window = self.screen.subwin(y_val - Config.padding - 1, 0, 0,
                                              0)
        self.statusbar = StatusBar(stdscreen)

        self.ebook_reader = "zathura"

    def __del__(self):
        self.close_connection()
        logging.debug("Connection closed after deleting object")

    def addir(self, Dir):
        if isinstance(Dir, Dirent) and Dir not in self.dirs:
            self.dirs.append(Dir)
            logging.debug("Added dir %s to object dirs", Dir.path)

        else:
            logging.error("Not a valid Dirent object %s", Dir)

    def addirs(self, uris):
        if not isinstance(uris, list) and not isinstance(uris, tuple):
            logging.error("Not a valid list or tuple")
        else:
            for uri in uris:
                logging.debug("Trying to create Dirent object from Dir %s",
                              uri)
                Dir = Dirent(uri)
                self.addir(Dir)

            self.commit_dirs_sql()
            logging.debug("Commited dirs to database")

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
        logging.debug("Table DIRS Created")

        self.cur.execute(
                "CREATE TABLE IF NOT EXISTS BOOKS(" "ID INTEGER PRIMARY KEY AUTOINCREMENT," "FOLDER         TEXT    NOT NULL," \
                "NAME           TEXT    NOT NULL," \
                "CATEGORY       TEXT," \
                "STATUS         INT," \
                "FAV            INT);")

        logging.debug("Table Books Created")

        self.cur.execute("CREATE INDEX IF NOT EXISTS idx_fav ON BOOKS (FAV);")
        logging.debug("Index on BOOKS (FAV) Created")

        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_category ON BOOKS (CATEGORY);")
        logging.debug("Index on BOOKS (CATEGORY) Created")

        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_status ON BOOKS (STATUS);")
        logging.debug("Index on BOOKS (STATUS) Created")

        self.cur.execute(
            "CREATE INDEX IF NOT EXISTS idx_folder ON BOOKS (FOLDER);")
        logging.debug("Index on BOOKS (FOLDER) Created")

        self.conn.commit()
        logging.debug("Changed commited to database")

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
            logging.debug("Dir %s Inserted to database", Dir.path)

        self.conn.commit()
        logging.debug("Changes commited to database")

    def commit_ebooks_sql(self):
        for ebook in self.ebooks:
            data = (ebook.name, ebook.folder, ebook.name, ebook.category,
                    ebook.status, ebook.fav)
            self.cur.execute(
                "INSERT OR REPLACE INTO BOOKS (ID, FOLDER, NAME, " \
                "CATEGORY, STATUS, FAV) " \
                "VALUES ((SELECT ID FROM BOOKS WHERE NAME = ?), ?, ?, ?, ?, ?);",
            data)
            logging.debug("Ebook %s Inserted to database", ebook.name)

        self.conn.commit()
        logging.debug("Changes commited to database")

    def ebooks_files_init(self):
        self.ebooks_files = [
            os.path.join(ebook.folder, ebook.name) for ebook in self.ebooks
        ]

    def del_dir(self, path):
        res = self.cur.execute("DELETE FROM DIRS WHERE PATH=?;", (path, ))
        res = self.cur.execute(
            f"DELETE FROM BOOKS WHERE FOLDER LIKE '{path}%';")
        logging.debug("Dir %s and all of its Ebooks Deleted from database",
                      path)
        self.conn.commit()
        logging.debug("Changes commited to database")
        for Dir in self.dirs:
            if Dir.path == path:
                self.dirs.remove(Dir)

        logging.debug("Dir %s removed from dirs", path)

    def del_dir_refetch(self, path):
        if self.statusbar.confirm(
                "Are you sure want to delete this directory? [y, n]",
                curses.color_pair(5)):
            self.del_dir(path)
            self.ebooks = self.fetch_ebooks()
            self.ebooks_files_init()
            self.statusbar.print("Directory has been deleted")
            sleep(.5)
            self.statusbar.print("Press ? to show help.")
            self.kill_rerun_main_menu()
        else:
            self.statusbar.print("Press ? to show help.")

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
        dirs = list()

        if not res:
            return dirs

        for row in res:
            Dir = Dirent()
            Dir.set_values(row[1], row[2])
            dirs.append(Dir)

        return dirs

    def kill_rerun_main_menu(self):
        self.make_menus()
        self.main_menu.kill()
        self.main_menu.init_window()
        if self.main_menu.display() == -1:
            self.exit(0)

    def make_menus(self):

        # reading menu
        reading_menu_items = [{
            "string": ebook.name,
            "enter_action": self.open_ebook,
            "args": [
                ebook,
            ],
            "type": "ebook",
            "take_action": self.take_action,
        } for ebook in self.fetch_ebooks(where="status=1")]
        reading_menu = Menu("reading", reading_menu_items, self.menu_window)

        # have read menu
        have_read_menu_items = [{
            "string": ebook.name,
            "enter_action": self.open_ebook,
            "args": [
                ebook,
            ],
            "type": "ebook",
            "take_action": self.take_action
        } for ebook in self.fetch_ebooks(where="status=2")]
        have_read_menu = Menu("have_read", have_read_menu_items,
                              self.menu_window)

        # haven't read menu
        havent_read_menu_items = [{
            "string": ebook.name,
            "enter_action": self.open_ebook,
            "args": [
                ebook,
            ],
            "type": "ebook",
            "take_action": self.take_action
        } for ebook in self.fetch_ebooks(where="status=0")]
        havent_read_menu = Menu("havent_read", havent_read_menu_items,
                                self.menu_window)

        # all menu
        all_menu_items = [{
            "string": ebook.name,
            "enter_action": self.open_ebook,
            "args": [
                ebook,
            ],
            "type": "ebook",
            "take_action": self.take_action
        } for ebook in self.fetch_ebooks()]
        all_menu = Menu("all", all_menu_items, self.menu_window)

        # folders men
        folders_menu_items = []
        self.dirs = self.fetch_dirs()
        for Dir in self.dirs:
            dir_ebooks = [
                ebook for ebook in self.fetch_ebooks(
                    where=f"folder like \'{Dir.path}%\'")
            ]
            dir_menu_items = [{
                "string": ebook.name,
                "enter_action": self.open_ebook,
                "args": [
                    ebook,
                ],
                "type": "ebook",
                "take_action": self.take_action
            } for ebook in dir_ebooks]
            dir_menu = Menu(Dir.path, dir_menu_items, self.menu_window)
            folders_menu_items.append({
                "string": Dir.path,
                "enter_action": dir_menu.display,
                "type": "dir",
                "take_action": self.take_action
            })

        folders_menu = Menu("folders", folders_menu_items, self.menu_window)

        # categories menu
        categories_menu_items = []
        categories_list = self.fetch_ebooks(key="category")
        for cat in categories_list:
            cat_ebooks = [
                ebook
                for ebook in self.fetch_ebooks(where="category=\'%s\'" % cat)
            ]
            cat_menu_items = [{
                "string": ebook.name,
                "enter_action": self.open_ebook,
                "args": [
                    ebook,
                ],
                "type": "ebook",
                "take_action": self.take_action
            } for ebook in cat_ebooks]
            cat_menu = Menu(cat, cat_menu_items, self.menu_window)
            categories_menu_items.append({
                "string": cat,
                "enter_action": cat_menu.display,
                "type": "cat",
                "take_action": self.take_action
            })

        categories_menu = Menu("categories", categories_menu_items,
                               self.menu_window)

        # favorites menu
        favorites_menu_items = [{
            "string": ebook.name,
            "enter_action": self.open_ebook,
            "args": [
                ebook,
            ],
            "type": "ebook",
            "take_action": self.take_action
        } for ebook in self.fetch_ebooks(where="fav=1")]
        favorites_menu = Menu("favorites", favorites_menu_items,
                              self.menu_window)

        # delete dir menu
        delete_dir_menu_item = [{
            "string": Dir.path,
            "enter_action": self.del_dir_refetch,
            "args": [
                Dir.path,
            ],
            "type": "dir",
            "take_action": self.take_action
        } for Dir in self.fetch_dirs()]
        delete_dir_menu = Menu("delete_dir", delete_dir_menu_item,
                               self.menu_window)

        main_menu_items = [
            {
                "string": "Reading",
                "enter_action": reading_menu.display,
                "type": "dir",
                "take_action": self.take_action
            },
            {
                "string": "Folders",
                "enter_action": folders_menu.display,
                "type": "dir",
                "take_action": self.take_action
            },
            {
                "string": "Favorites",
                "enter_action": favorites_menu.display,
                "type": "dir",
                "take_action": self.take_action
            },
            {
                "string": "Categories",
                "enter_action": categories_menu.display,
                "type": "dir",
                "take_action": self.take_action
            },
            {
                "string": "Have read",
                "enter_action": have_read_menu.display,
                "type": "dir",
                "take_action": self.take_action
            },
            {
                "string": "Haven't read",
                "enter_action": havent_read_menu.display,
                "type": "dir",
                "take_action": self.take_action
            },
            {
                "string": "All",
                "enter_action": all_menu.display,
                "type": "dir",
                "take_action": self.take_action
            },
            {
                "string": "Delete a directory",
                "enter_action": delete_dir_menu.display,
                "type": "dir",
                "take_action": self.take_action
            },
        ]

        self.main_menu = Menu("main", main_menu_items, self.menu_window)

    def open_ebook(self, ebook):
        uri = os.path.join(ebook.folder, ebook.name)
        self.change_ebook_status(ebook=ebook, status="Reading")

        cmd = "%s \"%s\" > /dev/null 2>&1" % (self.ebook_reader, uri)
        if not os.system(cmd):
            msg = "Couldn't open %s" % uri
            logging.error(msg)

        self.statusbar.print("Ebook added to Reading", curses.color_pair(4))
        self.kill_rerun_main_menu()

    def change_ebook_status(self,
                            status=None,
                            fav=None,
                            category=None,
                            ebook=None,
                            name=None):
        if name:
            for i in self.ebooks:
                if i.name == name:
                    ebook = i

        elif not ebook:
            return

        if fav:
            ebook.toggle_fav()
        elif status:
            if status == Ebook.STATUS_HAVE_NOT_READ and ebook.status in [
                    Ebook.STATUS_READING, Ebook.STATUS_HAVE_READ
            ]:
                ebook.status = Ebook.STATUS_HAVE_NOT_READ
            if status == Ebook.STATUS_HAVE_READ and ebook.status in [
                    Ebook.STATUS_HAVE_NOT_READ, Ebook.STATUS_READING
            ]:
                ebook.status = Ebook.STATUS_HAVE_READ

            else:
                ebook.set_status(status)
        elif category:
            ebook.set_category(category)

        for index, i in enumerate(self.ebooks):
            if i.name == ebook.name:
                self.ebooks[index] = ebook

        self.commit_ebooks_sql()
        logging.debug("Changed ebook %s status to reading", ebook.name)

    def scane(self):
        self.statusbar.print("Scanning for ebooks, Please wait.")
        mime = Mime()
        self.ebooks_files_init()

        for Dir in self.dirs:
            Dir.getfiles()
            for file in Dir.files:
                if mime.mime_type(
                        file
                ) == MIME_TYPE_EBOOK and file not in self.ebooks_files:
                    ebook = Ebook()
                    ebook.set_path(file)
                    self.ebooks.append(ebook)

        self.statusbar.print("Done.", curses.color_pair(4))

        self.update_db()

    def take_action(self, key, name=None, value=None):
        if key == "scane":
            self.scane()

        elif key == "toggle_mark":
            self.change_ebook_status(name=name, status=value)
            if value == "have_read":
                value = "Have read"
            else:
                value = "Haven't read"

            self.statusbar.print("Ebook marked as %s" % value,
                                 curses.color_pair(4))

        elif key == "toggle_fav":
            self.change_ebook_status(name=name, fav=True)
            self.statusbar.print("Ebook add to favorites",
                                 curses.color_pair(4))

        elif key == "add_category":
            self.change_ebook_status(name=name, category=value)
            self.statusbar.print("Ebook add to category %s" % value,
                                 curses.color_pair(4))

        elif key == "add_dir":
            if name[0] == "~":
                name = name.replace("~", os.getenv("HOME"))
            if not check_path(name):
                self.statusbar.print("Not a valid path", curses.color_pair(5))
                return

            Dir = Dirent(name)
            self.addir(Dir)
            self.scane()

        elif key == "print_status":
            self.statusbar.print(name)

        self.commit_ebooks_sql()
        self.commit_dirs_sql()
        self.kill_rerun_main_menu()

    def update_db(self):
        self.commit_dirs_sql()
        self.commit_ebooks_sql()

    def main(self):
        self.make_menus()
        self.statusbar.print("Press ? to show help.")
        if self.main_menu.display() == -1:
            self.exit(0)

    def exit(self, status):
        exit(status)
