"""A straight-line forecast. It is only shown when there is enough history, and it is never called actual revenue."""

from datetime import date

import numpy as np
import pandas as pd

from app.analytics.loader import bookings as load_bookings
from app.analytics.loader import payments as load_payments
from app.utils import add_month

MINIMUM_MONTHS = 8
DISCLAIMER = (
    "Predicted values are a straight-line estimate from past months. "
    "They are not actual bookings or actual revenue, and they are not a promise of future sales."
)


def build():
    today = date.today()
    current = f"{today.year:04d}-{today.month:02d}"
    booking_series = _monthly_bookings(current)
    revenue_series = _monthly_revenue(current)
    return {
        "disclaimer": DISCLAIMER,
        "bookings": _predict(booking_series, "booking demand"),
        "revenue": _predict(revenue_series, "collected revenue"),
    }


def _monthly_bookings(current_month):
    frame = load_bookings()
    if frame.empty:
        return {"labels": [], "values": []}
    frame = frame[frame["status"] != "cancelled"].copy()
    if frame.empty:
        return {"labels": [], "values": []}
    frame["month"] = pd.to_datetime(frame["event_date"]).dt.strftime("%Y-%m")
    frame = frame[frame["month"] <= current_month]
    return _fill(frame, "month", current_month, value_column=None)


def _monthly_revenue(current_month):
    frame = load_payments()
    if frame.empty:
        return {"labels": [], "values": []}
    frame["month"] = pd.to_datetime(frame["payment_date"]).dt.strftime("%Y-%m")
    frame = frame[frame["month"] <= current_month]
    return _fill(frame, "month", current_month, value_column="signed_amount")


def _fill(frame, column, current_month, value_column):
    if frame.empty:
        return {"labels": [], "values": []}
    grouped = frame.groupby(column).size() if value_column is None else frame.groupby(column)[value_column].sum()
    start = min(grouped.index)
    labels = []
    cursor = start
    while cursor <= current_month:
        labels.append(cursor)
        cursor = add_month(cursor, 1)
        if len(labels) > 120:
            break
    values = [float(grouped.get(label, 0.0)) for label in labels]
    return {"labels": labels, "values": values}


def _predict(series, name):
    labels = series["labels"]
    values = np.array(series["values"], dtype=float)
    if values.size < MINIMUM_MONTHS or float(np.sum(values)) <= 0:
        return {
            "available": False,
            "name": name,
            "message": (
                f"At least {MINIMUM_MONTHS} months of history with some activity are required "
                f"before a {name} forecast is shown."
            ),
        }
    try:
        from sklearn.linear_model import LinearRegression
        from sklearn.metrics import r2_score
    except ImportError:
        return {
            "available": False,
            "name": name,
            "message": "The forecast library is not installed, so no prediction was invented.",
        }
    x_values = np.arange(len(values), dtype=float).reshape(-1, 1)
    model = LinearRegression()
    model.fit(x_values, values)
    fitted = model.predict(x_values)
    score = float(r2_score(values, fitted))
    if score < 0.15:
        return {
            "available": False,
            "name": name,
            "message": (
                f"There are {len(values)} months of {name} history, but a straight line does not describe it "
                f"(R² {score:.2f}). Forecast numbers are hidden so they are not mistaken for a real outlook."
            ),
        }
    future_x = np.arange(len(values), len(values) + 3, dtype=float).reshape(-1, 1)
    predicted = np.maximum(model.predict(future_x), 0)
    reliability = "moderate" if score < 0.5 else "stronger"
    return {
        "available": True,
        "name": name,
        "history_labels": labels,
        "history_values": [round(float(item), 2) for item in values],
        "future_labels": [add_month(labels[-1], step) for step in (1, 2, 3)],
        "future_values": [round(float(item), 2) for item in predicted],
        "r2": round(score, 2),
        "reliability": reliability,
        "message": (
            f"This {name} line is predicted, not actual. "
            f"The straight-line fit is {reliability} (R² {score:.2f}). {DISCLAIMER}"
        ),
    }
