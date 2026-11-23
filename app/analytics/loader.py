"""Load SQLite rows into Pandas tables for the analytics functions."""

import numpy as np
import pandas as pd

from app.db import query_all


def dataframe(sql, params=None, numbers=()):
    rows = query_all(sql, params or ())
    if not rows:
        return pd.DataFrame()
    frame = pd.DataFrame(rows)
    for column in numbers:
        if column in frame.columns:
            frame[column] = pd.to_numeric(frame[column], errors="coerce").fillna(0.0)
    return frame


def payments(start=None, end=None):
    sql = """
        SELECT p.id, p.amount, p.payment_date, p.method, p.status,
               b.id AS booking_id, b.customer_id, b.city, b.event_type, b.total_amount,
               b.status AS booking_status, b.created_at AS booking_created,
               s.name AS service_name
        FROM payments p
        JOIN bookings b ON b.id = p.booking_id
        JOIN services s ON s.id = b.service_id
        WHERE 1=1
    """
    params = []
    if start:
        sql += " AND p.payment_date >= %s"
        params.append(start)
    if end:
        sql += " AND p.payment_date <= %s"
        params.append(end)
    frame = dataframe(sql, params, numbers=("amount", "total_amount"))
    return with_signed_amount(frame)


def with_signed_amount(frame):
    """Paid and partially paid add cash. Refunds subtract it. Pending adds nothing."""
    if frame.empty:
        return frame
    status = frame["status"].astype(str).to_numpy()
    amount = frame["amount"].to_numpy(dtype=float)
    signed = np.where(
        np.isin(status, ["paid", "partially_paid"]),
        amount,
        np.where(status == "refunded", -amount, np.zeros(len(amount), dtype=float)),
    )
    out = frame.copy()
    out["signed_amount"] = signed
    return out


def bookings(start=None, end=None, date_column="created_at"):
    column = "b.created_at" if date_column == "created_at" else "b.event_date"
    sql = f"""
        SELECT b.id, b.customer_id, b.city, b.event_type, b.event_date, b.created_at,
               b.total_amount, b.status, s.name AS service_name
        FROM bookings b
        JOIN services s ON s.id = b.service_id
        WHERE 1=1
    """
    params = []
    if start:
        sql += f" AND DATE({column}) >= %s"
        params.append(start)
    if end:
        sql += f" AND DATE({column}) <= %s"
        params.append(end)
    return dataframe(sql, params, numbers=("total_amount",))


def enquiries(start=None, end=None):
    sql = """
        SELECT e.id, e.status, e.event_type, e.city, e.created_at, e.event_date,
               b.created_at AS booking_created
        FROM enquiries e
        LEFT JOIN bookings b ON b.enquiry_id = e.id
        WHERE 1=1
    """
    params = []
    if start:
        sql += " AND DATE(e.created_at) >= %s"
        params.append(start)
    if end:
        sql += " AND DATE(e.created_at) <= %s"
        params.append(end)
    return dataframe(sql, params)


def customers(registered_through=None):
    sql = """
        SELECT c.id, c.full_name, c.city, c.registration_date,
               (SELECT COUNT(*) FROM bookings b WHERE b.customer_id = c.id) AS booking_count,
               COALESCE((
                   SELECT SUM(CASE
                       WHEN p.status IN ('paid','partially_paid') THEN p.amount
                       WHEN p.status = 'refunded' THEN -p.amount
                       ELSE 0 END)
                   FROM payments p
                   JOIN bookings b ON b.id = p.booking_id
                   WHERE b.customer_id = c.id
               ), 0) AS spending
        FROM customers c
        WHERE 1=1
    """
    params = []
    if registered_through:
        sql += " AND c.registration_date <= %s"
        params.append(registered_through)
    return dataframe(sql, params, numbers=("booking_count", "spending"))
