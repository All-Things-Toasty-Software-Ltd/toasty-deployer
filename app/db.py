# -*- coding: utf-8 -*-
# Part of Toasty Deployer. See LICENSE file for full copyright and licensing details.

import sqlite3

from config import Config


def get_connection():
    connection = sqlite3.connect(Config.DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    with get_connection() as connection:
        connection.execute('''
                           CREATE TABLE IF NOT EXISTS runs
                           (
                               id
                                   INTEGER
                                   PRIMARY
                                       KEY
                                   AUTOINCREMENT,
                               owner
                                   TEXT
                                   NOT
                                       NULL,
                               repo
                                   TEXT
                                   NOT
                                       NULL,
                               commit_sha
                                   TEXT
                                   NOT
                                       NULL,
                               status
                                   TEXT
                                   NOT
                                       NULL,
                               exit_code
                                   INTEGER
                                   DEFAULT
                                       -
                                           1,
                               logs
                                   TEXT
                                   DEFAULT
                                       '',
                               created_at
                                   TIMESTAMP
                                   DEFAULT
                                       CURRENT_TIMESTAMP
                           )
                           ''')
        connection.commit()


def create_run(owner, repo, commit_sha):
    with get_connection() as connection:
        cursor = connection.execute(
            "INSERT INTO runs (owner, repo, commit_sha, status, exit_code, logs) VALUES (?, ?, ?, ?, ?, ?)",
            (owner, repo, commit_sha, "running", -1, "")
        )
        connection.commit()
        return cursor.lastrowid


def update_run(run_id, status, exit_code, logs):
    with get_connection() as connection:
        connection.execute(
            "UPDATE runs SET status=?, exit_code=?, logs=? WHERE id=?",
            (status, exit_code, logs, run_id)
        )
        connection.commit()
