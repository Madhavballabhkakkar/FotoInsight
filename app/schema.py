"""Apply the SQLite schema. Used by the seed script and tests."""

from __future__ import annotations

import sqlite3
from pathlib import Path

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "database" / "schema_sqlite.sql"


def split_sql(text):
    statements = []
    buffer = []
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("--") or not stripped:
            continue
        buffer.append(line)
        if stripped.endswith(";"):
            statement = "\n".join(buffer).strip().rstrip(";").strip()
            if statement:
                statements.append(statement)
            buffer = []
    leftover = "\n".join(buffer).strip().rstrip(";").strip()
    if leftover:
        statements.append(leftover)
    return statements


class _Cursor:
    def __init__(self, conn):
        self._conn = conn
        self._cur = conn.cursor()
        self.lastrowid = None

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self._cur.close()

    def execute(self, sql, params=None):
        from app.db import adapt_params, normalize_sql

        self._cur.execute(normalize_sql(sql), adapt_params(params))
        self.lastrowid = self._cur.lastrowid
        return self

    def fetchone(self):
        row = self._cur.fetchone()
        return dict(row) if row else None

    def fetchall(self):
        return [dict(row) for row in self._cur.fetchall()]


class SqliteConnection:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")

    def cursor(self):
        return _Cursor(self._conn)

    def commit(self):
        self._conn.commit()

    def close(self):
        self._conn.close()

    def execute(self, sql, params=None):
        from app.db import adapt_params, normalize_sql

        return self._conn.execute(normalize_sql(sql), adapt_params(params))


def apply_schema(connection):
    script = SCHEMA_PATH.read_text(encoding="utf-8")
    for statement in split_sql(script):
        connection.execute(statement)
    connection.commit()


def connect_raw(path=None, **_ignored):
    """Open SQLite. Extra MySQL-style kwargs are ignored for compatibility."""
    if path is None:
        path = Path(__file__).resolve().parents[1] / "instance" / "fotoinsight.db"
    return SqliteConnection(path)
