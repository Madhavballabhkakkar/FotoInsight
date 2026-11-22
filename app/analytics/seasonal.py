"""When work happens: months, weekdays, and the wedding-season rule."""

import numpy as np
import pandas as pd

from app.analytics.loader import bookings as load_bookings
from app.constants import MONTH_NAMES, WEDDING_SEASONS, WEEKDAY_NAMES
from app.utils import month_keys


def analyse(start, end):
    frame = load_bookings(start, end, date_column="event_date")
    labels = month_keys(start, end)
    if not frame.empty:
        frame = frame[frame["status"] != "cancelled"].copy()
    if frame.empty:
        return {
            "recorded_by_month": {"labels": labels, "values": [0 for _ in labels]},
            "by_month_name": {"labels": MONTH_NAMES, "values": [0 for _ in MONTH_NAMES]},
            "heatmap": {"years": [], "months": MONTH_NAMES, "values": []},
            "by_quarter": {"labels": [], "values": []},
            "by_weekday": {"labels": WEEKDAY_NAMES, "values": [0 for _ in WEEKDAY_NAMES]},
            "weekend_share": None,
            "weekday_share": None,
            "seasons": [],
            "high_demand": [],
            "low_demand": [],
            "has_data": False,
        }

    event_day = pd.to_datetime(frame["event_date"])
    frame["month_key"] = event_day.dt.strftime("%Y-%m")
    frame["month_number"] = event_day.dt.month
    frame["year"] = event_day.dt.year
    frame["weekday"] = event_day.dt.dayofweek
    recorded = frame.groupby("month_key").size()
    recorded_by_month = {"labels": labels, "values": [int(recorded.get(label, 0)) for label in labels]}

    by_month = frame.groupby("month_number").size()
    by_month_name = {"labels": MONTH_NAMES, "values": [int(by_month.get(index, 0)) for index in range(1, 13)]}

    years = sorted(int(year) for year in frame["year"].unique())
    matrix = []
    for year in years:
        year_frame = frame[frame["year"] == year]
        counts = year_frame.groupby("month_number").size()
        matrix.append([int(counts.get(index, 0)) for index in range(1, 13)])

    frame["quarter"] = event_day.dt.year.astype(str) + "-Q" + event_day.dt.quarter.astype(str)
    quarter_counts = frame.groupby("quarter").size()
    by_quarter = {"labels": [str(item) for item in quarter_counts.index.tolist()], "values": [int(item) for item in quarter_counts.to_numpy()]}

    weekday_counts = frame.groupby("weekday").size()
    by_weekday = {"labels": WEEKDAY_NAMES, "values": [int(weekday_counts.get(index, 0)) for index in range(7)]}
    total = int(frame.shape[0])
    weekend = int(np.sum(frame["weekday"].to_numpy(dtype=int) >= 5))
    weekend_share = round(float(np.divide(weekend, total) * 100.0), 1) if total else None
    weekday_share = round(100.0 - weekend_share, 1) if weekend_share is not None else None

    seasons = []
    month_numbers = frame["month_number"].to_numpy(dtype=int)
    for name, months in WEDDING_SEASONS:
        count = int(np.sum(np.isin(month_numbers, list(months))))
        seasons.append({"name": name, "months": [MONTH_NAMES[item - 1] for item in months], "bookings": count})

    values = np.array(recorded_by_month["values"], dtype=float)
    high, low = _demand_periods(recorded_by_month["labels"], values)
    return {
        "recorded_by_month": recorded_by_month,
        "by_month_name": by_month_name,
        "heatmap": {"years": years, "months": MONTH_NAMES, "values": matrix},
        "by_quarter": by_quarter,
        "by_weekday": by_weekday,
        "weekend_share": weekend_share,
        "weekday_share": weekday_share,
        "seasons": seasons,
        "high_demand": high,
        "low_demand": low,
        "has_data": total > 0,
    }


def _demand_periods(labels, values):
    if values.size == 0 or float(np.sum(values)) == 0:
        return [], []
    mean = float(np.mean(values))
    spread = float(np.std(values))
    if spread < 0.01:
        return [], []
    high_line = mean + (0.5 * spread)
    low_line = mean - (0.5 * spread)
    high = [label for label, value in zip(labels, values) if value >= high_line and value > 0]
    low = [label for label, value in zip(labels, values) if value <= low_line]
    if not high:
        high = [labels[int(np.argmax(values))]]
    return high, low


def created_by_month(start, end):
    """Bookings recorded in the office during the range, used by the overview bar chart."""
    frame = load_bookings(start, end, date_column="created_at")
    labels = month_keys(start, end)
    if frame.empty:
        return {"labels": labels, "values": [0 for _ in labels]}
    frame = frame[frame["status"] != "cancelled"].copy()
    if frame.empty:
        return {"labels": labels, "values": [0 for _ in labels]}
    frame["month"] = pd.to_datetime(frame["created_at"]).dt.strftime("%Y-%m")
    grouped = frame.groupby("month").size()
    return {"labels": labels, "values": [int(grouped.get(label, 0)) for label in labels]}
