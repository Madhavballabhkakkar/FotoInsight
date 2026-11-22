"""Small helpers used across models, pages, and reports."""

import re
from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from app.constants import STATUS_LABELS
from app.errors import AppError


def clean_row(row):
    if row is None:
        return None
    cleaned = {}
    for key, value in row.items():
        if isinstance(value, Decimal):
            cleaned[key] = float(value.quantize(Decimal("0.01")))
        elif isinstance(value, datetime):
            cleaned[key] = value.strftime("%Y-%m-%d %H:%M:%S")
        elif isinstance(value, date):
            cleaned[key] = value.isoformat()
        else:
            cleaned[key] = value
    return cleaned


def clean_rows(rows):
    return [clean_row(row) for row in rows]


def like(term):
    escaped = term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def parse_page(args, default_per_page=10):
    try:
        page = int(args.get("page", 1))
    except (TypeError, ValueError):
        page = 1
    try:
        per_page = int(args.get("per_page", default_per_page))
    except (TypeError, ValueError):
        per_page = default_per_page
    page = max(1, page)
    per_page = min(50, max(5, per_page))
    return page, per_page


def pagination(total, page, per_page):
    pages = max(1, (total + per_page - 1) // per_page) if total else 1
    page = min(page, pages)
    return {"page": page, "per_page": per_page, "total": total, "pages": pages, "offset": (page - 1) * per_page}


def label(status):
    return STATUS_LABELS.get(status, str(status or "").replace("_", " ").title())


def format_inr(value):
    try:
        amount = Decimal(str(value if value is not None else 0)).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        return "INR 0"
    sign = "-" if amount < 0 else ""
    whole = int(abs(amount))
    fraction = int((abs(amount) - Decimal(whole)) * 100)
    text = str(whole)
    if len(text) > 3:
        head, tail = text[:-3], text[-3:]
        groups = []
        while len(head) > 2:
            groups.append(head[-2:])
            head = head[:-2]
        if head:
            groups.append(head)
        text = ",".join(reversed(groups)) + "," + tail
    if fraction:
        return f"{sign}INR {text}.{fraction:02d}"
    return f"{sign}INR {text}"


def round_money(value):
    if value is None:
        return 0.0
    return float(Decimal(str(value)).quantize(Decimal("0.01")))


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", (value or "").lower()).strip("-")
    return slug or "service"


def code_for(prefix, row_id):
    return f"{prefix}-{int(row_id):05d}"


def as_date(value):
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError as exc:
        raise AppError("Use a real date in YYYY-MM-DD format.") from exc


def month_keys(start, end):
    keys = []
    year, month = start.year, start.month
    while (year, month) <= (end.year, end.month):
        keys.append(f"{year:04d}-{month:02d}")
        month += 1
        if month == 13:
            month = 1
            year += 1
    return keys


def add_month(year_month, steps):
    year, month = map(int, year_month.split("-"))
    month += steps
    year += (month - 1) // 12
    month = (month - 1) % 12 + 1
    return f"{year:04d}-{month:02d}"
