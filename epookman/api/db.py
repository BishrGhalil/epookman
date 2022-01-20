#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of epookman, the console ebook manager.
# License: MIT, see the file "LICENCS" for details.
"""Epookman database handling functions"""

import logging
import sqlite3

from epookman.api.dirent import Dirent
from epookman.api.ebook import Ebook


# Connect and Disconnect functions
def connect(db_path):
    logging.info("Connecting to database")
    conn = sqlite3.connect(db_path)
    logging.info("Connected to database")
    return conn


def close_connection(conn):
    conn.close()
    logging.info("Connection to database has been closed.")


# Create tables functions


def create_dirs_table(conn):
    cur = conn.cursor()
    cur.execute(
            "CREATE TABLE IF NOT EXISTS DIRS(" \
            "ID INTEGER PRIMARY KEY AUTOINCREMENT," \
            "PATH           TEXT NOT NULL," \
            "RECURS         INT NOT NULL);"
    )
    logging.debug("Table DIRS Created")

    conn.commit()


def create_ebooks_table(conn):
    cur = conn.cursor()
    cur.execute(
        "CREATE TABLE IF NOT EXISTS EBOOKS(" \
        "ID INTEGER PRIMARY KEY AUTOINCREMENT," \
        "FOLDER         TEXT    NOT NULL," \
        "NAME           TEXT    NOT NULL," \
        "CATEGORY       TEXT," \
        "STATUS         INT," \
        "FAV            INT);")

    logging.debug("Table Books Created")
    conn.commit()


def create_ebooks_index(conn, index_key):
    cur = conn.cursor()
    cur.execute(
        "CREATE INDEX IF NOT EXISTS " \
        f"idx_{index_key.lower()} ON EBOOKS ({index_key.upper()});"
    )

    logging.debug(f"Index on EBOOKS ({index_key.upper()}) Created")
    conn.commit()


def create_ebooks_indexes(conn):
    indexes = ["fav", "category", "status", "folder"]
    for index_key in indexes:
        create_ebooks_index(conn, index_key)


def create_tables(conn):
    create_dirs_table(conn)
    create_ebooks_table(conn)
    create_ebooks_indexes(conn)


# Insert and update functions


def commit_dirs(conn, dirs):
    for Dir in dirs:
        commit_dir(conn, Dir)


def commit_dir(conn, Dir):
    cur = conn.cursor()
    data = (Dir.path, Dir.path, Dir.recurs)
    cur.execute(
        "INSERT OR REPLACE \
        INTO DIRS (ID, PATH, RECURS) \
        VALUES \
        ((SELECT ID FROM DIRS WHERE PATH = ?), ?, ?);", data)

    logging.debug("Dir %s Inserted to database", Dir.path)

    conn.commit()


def commit_ebooks(conn, ebooks):
    for ebook in ebooks:
        commit_ebook(conn, ebook)
        conn.commit()


def commit_ebook(conn, ebook):
    cur = conn.cursor()
    data = (ebook.name, ebook.folder, ebook.name, ebook.category, ebook.status,
            ebook.fav)
    cur.execute(
        "INSERT OR REPLACE "\
        "INTO EBOOKS (ID, FOLDER, NAME, " \
        "CATEGORY, STATUS, FAV) " \
        "VALUES ((SELECT ID FROM EBOOKS WHERE NAME = ?), ?, ?, ?, ?, ?);",
        data)

    logging.debug(f"Ebook: {data} Inserted to database")

    conn.commit()


def update_db(conn, dirs, ebooks):
    commit_dirs(conn, dirs)
    commit_ebooks(conn, ebooks)


# Delete functions


def del_dir(conn, path):
    cur = conn.cursor()
    cur.execute("DELETE FROM DIRS WHERE PATH=?;", (path, ))
    conn.commit()
    logging.debug("Dir %s has been deleted from database", path)


def del_ebooks(conn, directory=None, name=None, category=None):
    cur = conn.cursor()
    if directory:
        cur.execute(f"DELETE FROM EBOOKS WHERE FOLDER LIKE '{directory}%';")
    elif name:
        cur.execute(f"DELETE FROM EBOOKS WHERE NAME LIKE '{name}';")
    elif category:
        cur.execute(f"DELETE FROM EBOOKS WHERE CATEGORY LIKE '{category}';")

    conn.commit()
    logging.debug("Books have been deleted from database")


# Fetching functions


def fetch_ebooks(conn, key="*", where=None, sort_clause=None):
    if not sort_clause:
        sort_clause = "ORDER BY NAME, FAV DESC"

    if not where:
        query = f"SELECT DISTINCT {key} FROM EBOOKS {sort_clause};"

    else:
        query = f"SELECT DISTINCT {key} FROM EBOOKS WHERE {where} {sort_clause};"

    cur = conn.cursor()
    res = cur.execute(query)
    ebooks = list()

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


def fetch_dirs(conn):
    cur = conn.cursor()
    res = cur.execute("SELECT DISTINCT * FROM DIRS ORDER BY PATH;")
    dirs = list()

    if not res:
        return dirs

    for row in res:
        Dir = Dirent()
        Dir.set_values(row[1], row[2])
        dirs.append(Dir)

    return dirs
