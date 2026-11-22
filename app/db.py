"""Small MySQL helper. Routes and models share one connection per request."""

import ssl
from contextlib import contextmanager

import pymysql
from flask import current_app, g
from pymysql.err import OperationalError


def get_db():
    if "db" not in g:
        try:
            connect_kwargs = {
                "host": current_app.config["MYSQL_HOST"],
                "port": current_app.config["MYSQL_PORT"],
                "user": current_app.config["MYSQL_USER"],
                "password": current_app.config["MYSQL_PASSWORD"],
                "database": current_app.config["MYSQL_DATABASE"],
                "cursorclass": pymysql.cursors.DictCursor,
                "autocommit": False,
                "charset": "utf8mb4",
                "connect_timeout": 10,
                "read_timeout": 30,
                "write_timeout": 30,
            }
            if current_app.config.get("MYSQL_SSL"):
                # Free cloud MySQL often needs TLS without a custom CA file.
                connect_kwargs["ssl"] = ssl._create_unverified_context()
            g.db = pymysql.connect(**connect_kwargs)
        except OperationalError as exc:
            raise OperationalError(
                exc.args[0] if exc.args else 2003,
                "The database could not be reached. Check that MySQL is running and .env is correct.",
            ) from exc
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_all(sql, params=None):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()


def query_one(sql, params=None):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchone()


def execute(sql, params=None, commit=True):
    db = get_db()
    with db.cursor() as cur:
        cur.execute(sql, params or ())
        last_id = cur.lastrowid
    if commit:
        db.commit()
    return last_id


def tx_query_all(db, sql, params=None):
    with db.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchall()


def tx_query_one(db, sql, params=None):
    with db.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.fetchone()


def tx_execute(db, sql, params=None):
    with db.cursor() as cur:
        cur.execute(sql, params or ())
        return cur.lastrowid


@contextmanager
def transaction():
    db = get_db()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
