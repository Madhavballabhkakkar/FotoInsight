"""SQLite helper. Routes and models share one connection per request."""

from __future__ import annotations

import re
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

from flask import current_app, g

# Re-export so models do not depend on MySQL drivers.
IntegrityError = sqlite3.IntegrityError
OperationalError = sqlite3.OperationalError


def adapt_params(params):
    if not params:
        return ()
    adapted = []
    for value in params:
        if isinstance(value, Decimal):
            adapted.append(float(value))
        elif isinstance(value, datetime):
            adapted.append(value.strftime("%Y-%m-%d %H:%M:%S"))
        elif isinstance(value, date):
            adapted.append(value.isoformat())
        else:
            adapted.append(value)
    return tuple(adapted)


def normalize_sql(sql: str) -> str:
    """Translate the project's MySQL-style SQL into SQLite."""
    out = sql
    out = out.replace("%s", "?")
    out = re.sub(r"\s+FOR UPDATE\b", "", out, flags=re.IGNORECASE)
    out = re.sub(r"\bCURDATE\(\)", "date('now')", out, flags=re.IGNORECASE)
    out = re.sub(
        r"DATE_FORMAT\(([^,]+),\s*'%%Y-%%m'\)",
        r"strftime('%Y-%m', \1)",
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(
        r"DATE_FORMAT\(([^,]+),\s*'%Y-%m'\)",
        r"strftime('%Y-%m', \1)",
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(
        r"\bYEAR\(([^)]+)\)",
        r"CAST(strftime('%Y', \1) AS INTEGER)",
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(
        r"\bMONTH\(([^)]+)\)",
        r"CAST(strftime('%m', \1) AS INTEGER)",
        out,
        flags=re.IGNORECASE,
    )
    out = re.sub(r"CAST\(([^)]+) AS CHAR\)", r"CAST(\1 AS TEXT)", out, flags=re.IGNORECASE)
    out = out.replace("ESCAPE '\\\\'", "ESCAPE '\\'")
    return out


def sqlite_path():
    configured = current_app.config.get("SQLITE_PATH")
    path = Path(configured)
    if not path.is_absolute():
        root = Path(current_app.root_path).resolve().parent
        path = root / path
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def get_db():
    if "db" not in g:
        try:
            path = sqlite_path()
            conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON")
            g.db = conn
        except sqlite3.Error as exc:
            raise OperationalError(
                "The database could not be reached. Check SQLITE_PATH and that the app can write its data folder."
            ) from exc
    return g.db


def close_db(_error=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def query_all(sql, params=None):
    cur = get_db().execute(normalize_sql(sql), adapt_params(params))
    return [dict(row) for row in cur.fetchall()]


def query_one(sql, params=None):
    cur = get_db().execute(normalize_sql(sql), adapt_params(params))
    row = cur.fetchone()
    return dict(row) if row else None


def execute(sql, params=None, commit=True):
    db = get_db()
    cur = db.execute(normalize_sql(sql), adapt_params(params))
    last_id = cur.lastrowid
    if commit:
        db.commit()
    return last_id


def tx_query_all(db, sql, params=None):
    cur = db.execute(normalize_sql(sql), adapt_params(params))
    return [dict(row) for row in cur.fetchall()]


def tx_query_one(db, sql, params=None):
    cur = db.execute(normalize_sql(sql), adapt_params(params))
    row = cur.fetchone()
    return dict(row) if row else None


def tx_execute(db, sql, params=None):
    cur = db.execute(normalize_sql(sql), adapt_params(params))
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
