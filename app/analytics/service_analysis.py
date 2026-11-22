"""Which services are asked for, booked, and actually paid for."""

import numpy as np
import pandas as pd

from app.analytics.loader import bookings as load_bookings
from app.analytics.loader import dataframe
from app.analytics.loader import enquiries as load_enquiries
from app.analytics.loader import payments as load_payments
from app.utils import month_keys, round_money


def analyse(start, end):
    services = dataframe("SELECT id, name, status FROM services ORDER BY sort_order, name")
    enquiry_frame = load_enquiries(start, end)
    booking_frame = load_bookings(start, end, date_column="created_at")
    payment_frame = load_payments(start, end)
    names = [] if services.empty else [str(name) for name in services["name"].tolist()]
    if not names and enquiry_frame.empty and booking_frame.empty:
        return {"rows": [], "most_popular": None, "least_popular": None, "highest_revenue": None, "most_booked": None, "demand_trend": {"labels": [], "datasets": []}, "has_data": False}

    enquiry_counts = {} if enquiry_frame.empty else enquiry_frame.groupby(enquiry_frame["event_type"].fillna("Unknown")).size().to_dict()
    if booking_frame.empty:
        kept = booking_frame
    else:
        kept = booking_frame[booking_frame["status"] != "cancelled"]
    booking_counts = {} if kept.empty else kept.groupby("service_name").size().to_dict()
    averages = {}
    if not kept.empty:
        for name, subset in kept.groupby("service_name"):
            averages[str(name)] = round_money(float(np.mean(subset["total_amount"].to_numpy(dtype=float))))
    revenue = {}
    if not payment_frame.empty:
        grouped = payment_frame.groupby("service_name")["signed_amount"].sum()
        revenue = {str(key): round_money(value) for key, value in grouped.items()}

    rows = []
    seen = set(names)
    seen.update(enquiry_counts)
    seen.update(booking_counts)
    seen.update(revenue)
    for name in sorted(seen):
        rows.append({
            "service": name,
            "enquiries": int(enquiry_counts.get(name, 0)),
            "bookings": int(booking_counts.get(name, 0)),
            "revenue": revenue.get(name, 0.0),
            "average_booking_value": averages.get(name),
        })
    rows.sort(key=lambda item: (-item["revenue"], -item["bookings"], -item["enquiries"], item["service"]))

    def pick(key, reverse=True, ignore_zero=True):
        pool = [row for row in rows if (row[key] or 0) > 0] if ignore_zero else list(rows)
        if not pool:
            return None
        best = max(pool, key=lambda item: item[key]) if reverse else min(pool, key=lambda item: item[key])
        tied = [row["service"] for row in pool if row[key] == best[key]]
        return ", ".join(tied)

    active_names = set(names)
    least_pool = [row for row in rows if row["service"] in active_names] or rows
    least = None
    if least_pool and any(row["enquiries"] or row["bookings"] for row in least_pool):
        lowest = min(row["enquiries"] for row in least_pool)
        least = ", ".join(row["service"] for row in least_pool if row["enquiries"] == lowest)

    demand = _demand(kept, start, end)
    has_data = any(row["enquiries"] or row["bookings"] or row["revenue"] for row in rows)
    return {
        "rows": rows,
        "most_popular": pick("enquiries"),
        "least_popular": least,
        "highest_revenue": pick("revenue"),
        "most_booked": pick("bookings"),
        "demand_trend": demand,
        "has_data": has_data,
    }


def _demand(bookings, start, end):
    labels = month_keys(start, end)
    if bookings.empty:
        return {"labels": labels, "datasets": []}
    frame = bookings.copy()
    # Same date as the booking counts in the table: the day the booking was recorded.
    # Event-date seasonality is calculated separately in seasonal.py.
    frame["month"] = pd.to_datetime(frame["created_at"]).dt.strftime("%Y-%m")
    totals = frame.groupby("service_name").size().sort_values(ascending=False)
    datasets = []
    for name in list(totals.index)[:4]:
        subset = frame[frame["service_name"] == name]
        grouped = subset.groupby("month").size()
        datasets.append({
            "label": str(name),
            "values": [int(grouped.get(label, 0)) for label in labels],
        })
    return {"labels": labels, "datasets": datasets}
