"""Compulsory local persistence: JSON, CSV, and Excel files under /data."""

from __future__ import annotations

import json
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import pandas as pd

from app.db import query_all

DATA_DIR = Path(__file__).resolve().parents[1] / "data"

DATASETS = (
    ("customers", "SELECT * FROM customers ORDER BY id"),
    ("enquiries", "SELECT * FROM enquiries ORDER BY id"),
    ("bookings", "SELECT * FROM bookings ORDER BY id"),
    ("payments", "SELECT * FROM payments ORDER BY id"),
    ("services", "SELECT * FROM services ORDER BY id"),
    ("projects", "SELECT * FROM projects ORDER BY id"),
)


def ensure_data_dir():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    return DATA_DIR


def _json_safe(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, datetime):
        return value.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return value


def _rows(sql):
    return [{key: _json_safe(value) for key, value in row.items()} for row in query_all(sql)]


def _frame(rows):
    if not rows:
        return pd.DataFrame()
    return pd.DataFrame(rows)


def export_all():
    """Write every main table to JSON, CSV, and Excel. Returns a summary for the UI."""
    ensure_data_dir()
    stamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    written = []
    bundle = {"exported_at": stamp, "tables": {}}

    for name, sql in DATASETS:
        rows = _rows(sql)
        bundle["tables"][name] = rows
        frame = _frame(rows)

        json_path = DATA_DIR / f"{name}.json"
        csv_path = DATA_DIR / f"{name}.csv"
        xlsx_path = DATA_DIR / f"{name}.xlsx"

        json_path.write_text(json.dumps(rows, indent=2, ensure_ascii=False), encoding="utf-8")
        frame.to_csv(csv_path, index=False)
        frame.to_excel(xlsx_path, index=False)

        written.append({
            "name": name,
            "rows": len(rows),
            "json": str(json_path.name),
            "csv": str(csv_path.name),
            "excel": str(xlsx_path.name),
        })

    bundle_path = DATA_DIR / "fotoinsight_bundle.json"
    bundle_path.write_text(json.dumps(bundle, indent=2, ensure_ascii=False), encoding="utf-8")

    workbook_path = DATA_DIR / "fotoinsight_all.xlsx"
    with pd.ExcelWriter(workbook_path) as writer:
        for item in written:
            frame = _frame(bundle["tables"][item["name"]])
            sheet = item["name"][:31]
            frame.to_excel(writer, sheet_name=sheet, index=False)

    return {
        "ok": True,
        "exported_at": stamp,
        "folder": str(DATA_DIR),
        "tables": written,
        "bundle_json": bundle_path.name,
        "bundle_excel": workbook_path.name,
    }


def list_local_files():
    ensure_data_dir()
    files = []
    for path in sorted(DATA_DIR.iterdir()):
        if path.name.startswith("."):
            continue
        files.append({
            "name": path.name,
            "size": path.stat().st_size,
            "kind": path.suffix.lstrip(".").upper() or "FILE",
        })
    return files


def load_json_table(name):
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        return []
    return json.loads(path.read_text(encoding="utf-8"))


def load_bundle():
    path = DATA_DIR / "fotoinsight_bundle.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))
