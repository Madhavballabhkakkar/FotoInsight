"""Revenue from recorded payments only. A booking total is not treated as cash."""

import calendar

import numpy as np
import pandas as pd

from app.analytics.loader import bookings as load_bookings
from app.analytics.loader import payments as load_payments
from app.utils import month_keys, round_money


def _series(frame, column, labels):
    if frame.empty:
        values = [0.0 for _ in labels]
    else:
        frame = frame.copy()
        frame["bucket"] = pd.to_datetime(frame[column]).dt.strftime("%Y-%m")
        grouped = frame.groupby("bucket")["signed_amount"].sum()
        values = [round_money(grouped.get(label, 0.0)) for label in labels]
    return {"labels": labels, "values": values}


def _growth(labels, values, end):
    """Compare the last two full months. A month still in progress is left out."""
    if len(labels) < 2:
        return None
    usable = list(zip(labels, values))
    last_day = calendar.monthrange(end.year, end.month)[1]
    if end.day < last_day and len(usable) >= 3:
        usable = usable[:-1]
    current_label, current = usable[-1]
    previous_label, previous = usable[-2]
    if previous <= 0:
        return None
    change = float(np.divide(current - previous, previous) * 100.0)
    return {
        "current_label": current_label,
        "previous_label": previous_label,
        "current": round_money(current),
        "previous": round_money(previous),
        "percent": round(change, 1),
    }


def analyse(start, end):
    frame = load_payments(start, end)
    labels = month_keys(start, end)
    if frame.empty:
        monthly = {"labels": labels, "values": [0.0 for _ in labels]}
        return {
            "total_revenue": 0.0,
            "gross_collected": 0.0,
            "refunds": 0.0,
            "pending_not_counted": 0.0,
            "average_booking_value": None,
            "bookings_in_average": 0,
            "growth": None,
            "monthly": monthly,
            "quarterly": {"labels": [], "values": []},
            "yearly": {"labels": [], "values": []},
            "by_service": {"labels": [], "values": []},
            "by_location": {"labels": [], "values": []},
            "has_data": False,
        }

    signed = frame["signed_amount"].to_numpy(dtype=float)
    collected_mask = np.isin(frame["status"].astype(str).to_numpy(), ["paid", "partially_paid"])
    refund_mask = frame["status"].astype(str).to_numpy() == "refunded"
    pending_mask = frame["status"].astype(str).to_numpy() == "pending"
    total = round_money(np.sum(signed))
    gross = round_money(np.sum(frame.loc[collected_mask, "amount"].to_numpy(dtype=float))) if collected_mask.any() else 0.0
    refunds = round_money(np.sum(frame.loc[refund_mask, "amount"].to_numpy(dtype=float))) if refund_mask.any() else 0.0
    pending = round_money(np.sum(frame.loc[pending_mask, "amount"].to_numpy(dtype=float))) if pending_mask.any() else 0.0

    monthly = _series(frame, "payment_date", labels)
    growth = _growth(monthly["labels"], monthly["values"], end)

    dated = frame.copy()
    dated["paid_on"] = pd.to_datetime(dated["payment_date"])
    dated["quarter"] = dated["paid_on"].dt.year.astype(str) + "-Q" + dated["paid_on"].dt.quarter.astype(str)
    dated["year"] = dated["paid_on"].dt.year.astype(str)
    quarterly = _grouped(dated, "quarter")
    yearly = _grouped(dated, "year")
    by_service = _grouped(dated, "service_name")
    by_location = _grouped(dated, "city")

    booking_frame = load_bookings(start, end, date_column="created_at")
    average = None
    counted = 0
    if not booking_frame.empty:
        active = booking_frame[booking_frame["status"] != "cancelled"]
        counted = int(active.shape[0])
        if counted:
            average = round_money(float(np.mean(active["total_amount"].to_numpy(dtype=float))))

    return {
        "total_revenue": total,
        "gross_collected": gross,
        "refunds": refunds,
        "pending_not_counted": pending,
        "average_booking_value": average,
        "bookings_in_average": counted,
        "growth": growth,
        "monthly": monthly,
        "quarterly": quarterly,
        "yearly": yearly,
        "by_service": by_service,
        "by_location": by_location,
        "has_data": bool(np.any(signed != 0) or pending > 0),
    }


def _grouped(frame, column):
    grouped = frame.groupby(column)["signed_amount"].sum().sort_values(ascending=False)
    return {
        "labels": [str(label) for label in grouped.index.tolist()],
        "values": [round_money(value) for value in grouped.to_numpy(dtype=float)],
    }
