"""City-wise enquiries, bookings, revenue, and conversion."""

import numpy as np
import pandas as pd

from app.analytics.loader import bookings as load_bookings
from app.analytics.loader import enquiries as load_enquiries
from app.analytics.loader import payments as load_payments
from app.constants import ELIGIBLE_ENQUIRY_STATUSES
from app.utils import round_money


def analyse(start, end):
    enquiry_frame = load_enquiries(start, end)
    booking_frame = load_bookings(start, end, date_column="created_at")
    payment_frame = load_payments(start, end)
    if not booking_frame.empty:
        booking_frame = booking_frame[booking_frame["status"] != "cancelled"].copy()

    cities = set()
    enquiry_groups = {}
    if not enquiry_frame.empty:
        temporary = enquiry_frame.copy()
        temporary["city"] = temporary["city"].fillna("Unknown").replace("", "Unknown")
        cities.update(temporary["city"].unique())
        for city, subset in temporary.groupby("city"):
            status = subset["status"].astype(str)
            converted = int(np.sum((status == "converted").to_numpy()))
            eligible = int(np.sum(status.isin(ELIGIBLE_ENQUIRY_STATUSES).to_numpy()))
            enquiry_groups[str(city)] = {
                "enquiries": int(subset.shape[0]),
                "converted": converted,
                "eligible": eligible,
            }
    booking_groups = {}
    if not booking_frame.empty:
        cities.update(booking_frame["city"].fillna("Unknown").unique())
        booking_groups = booking_frame.groupby(booking_frame["city"].fillna("Unknown")).size().to_dict()
    revenue_groups = {}
    if not payment_frame.empty:
        cities.update(payment_frame["city"].fillna("Unknown").unique())
        grouped = payment_frame.groupby(payment_frame["city"].fillna("Unknown"))["signed_amount"].sum()
        revenue_groups = {str(key): round_money(value) for key, value in grouped.items()}

    rows = []
    for city in cities:
        key = str(city)
        info = enquiry_groups.get(key, {"enquiries": 0, "converted": 0, "eligible": 0})
        rate = None
        if info["eligible"] > 0:
            rate = round(float(np.divide(info["converted"], info["eligible"]) * 100.0), 1)
        rows.append({
            "city": key,
            "enquiries": info["enquiries"],
            "bookings": int(booking_groups.get(key, booking_groups.get(city, 0)) or 0),
            "revenue": revenue_groups.get(key, 0.0),
            "conversion_rate": rate,
        })
    rows.sort(key=lambda item: (-item["bookings"], -item["revenue"], item["city"]))
    booking_total = int(sum(row["bookings"] for row in rows))
    top = rows[0] if rows and rows[0]["bookings"] > 0 else None
    share = None
    if top and booking_total:
        share = round(float(np.divide(top["bookings"], booking_total) * 100.0), 1)
    return {
        "rows": rows,
        "top_city": top["city"] if top else None,
        "top_city_share": share,
        "has_data": bool(rows) and any(row["enquiries"] or row["bookings"] or row["revenue"] for row in rows),
    }
