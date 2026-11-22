"""Apply database/schema.sql. Used by the seed script and the tests."""

from pathlib import Path

import pymysql

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "database" / "schema.sql"


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


def apply_schema(connection):
    script = SCHEMA_PATH.read_text(encoding="utf-8")
    with connection.cursor() as cur:
        for statement in split_sql(script):
            cur.execute(statement)
    connection.commit()


def connect_raw(host, port, user, password, database):
    return pymysql.connect(
        host=host,
        port=int(port),
        user=user,
        password=password,
        database=database,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        charset="utf8mb4",
    )
