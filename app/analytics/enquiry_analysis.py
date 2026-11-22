"""Enquiry conversion. The eligible statuses are defined in app.constants."""

import numpy as np
import pandas as pd

from app.analytics.loader import enquiries as load_enquiries
from app.constants import CONVERSION_DEFINITION, ELIGIBLE_ENQUIRY_STATUSES, OPEN_ENQUIRY_STATUSES
from app.utils import label, month_keys


def _rate(converted, eligible):
    if eligible <= 0:
        return None
    return round(float(np.divide(converted, eligible) * 100.0), 1)


def analyse(start, end):
    frame = load_enquiries(start, end)
    definition = CONVERSION_DEFINITION
    if frame.empty:
        return {
            "total": 0,
            "converted": 0,
            "rejected": 0,
            "pending": 0,
            "eligible": 0,
            "new_excluded": 0,
            "conversion_rate": None,
            "average_conversion_days": None,
            "definition": definition,
            "by_status": {"labels": [], "values": []},
            "monthly_rate": {"labels": month_keys(start, end), "values": [None for _ in month_keys(start, end)]},
            "by_service": [],
            "has_data": False,
        }

    status = frame["status"].astype(str)
    total = int(frame.shape[0])
    converted = int(np.sum((status == "converted").to_numpy()))
    rejected = int(np.sum((status == "rejected").to_numpy()))
    pending = int(np.sum(status.isin(OPEN_ENQUIRY_STATUSES).to_numpy()))
    eligible_mask = status.isin(ELIGIBLE_ENQUIRY_STATUSES).to_numpy()
    eligible = int(np.sum(eligible_mask))
    new_excluded = int(np.sum((status == "new").to_numpy()))
    rate = _rate(converted, eligible)

    counts = status.value_counts()
    by_status = {
        "labels": [label(item) for item in counts.index.tolist()],
        "values": [int(item) for item in counts.to_numpy()],
    }

    working = frame.copy()
    working["month"] = pd.to_datetime(working["created_at"]).dt.strftime("%Y-%m")
    monthly_labels = month_keys(start, end)
    monthly_values = []
    for month in monthly_labels:
        subset = working[working["month"] == month]
        if subset.empty:
            monthly_values.append(None)
            continue
        subset_status = subset["status"].astype(str)
        monthly_values.append(_rate(
            int(np.sum((subset_status == "converted").to_numpy())),
            int(np.sum(subset_status.isin(ELIGIBLE_ENQUIRY_STATUSES).to_numpy())),
        ))

    service_rows = []
    for event_type, subset in working.groupby(working["event_type"].fillna("Unknown")):
        subset_status = subset["status"].astype(str)
        service_converted = int(np.sum((subset_status == "converted").to_numpy()))
        service_eligible = int(np.sum(subset_status.isin(ELIGIBLE_ENQUIRY_STATUSES).to_numpy()))
        service_rows.append({
            "service": str(event_type),
            "total": int(subset.shape[0]),
            "converted": service_converted,
            "eligible": service_eligible,
            "conversion_rate": _rate(service_converted, service_eligible),
        })
    service_rows.sort(key=lambda item: (item["conversion_rate"] is None, -(item["conversion_rate"] or 0), -item["total"]))

    average_days = _average_days(working)
    return {
        "total": total,
        "converted": converted,
        "rejected": rejected,
        "pending": pending,
        "eligible": eligible,
        "new_excluded": new_excluded,
        "conversion_rate": rate,
        "average_conversion_days": average_days,
        "definition": definition,
        "by_status": by_status,
        "monthly_rate": {"labels": monthly_labels, "values": monthly_values},
        "by_service": service_rows,
        "has_data": total > 0,
    }


def _average_days(frame):
    converted = frame[frame["status"].astype(str) == "converted"].copy()
    if converted.empty or "booking_created" not in converted.columns:
        return None
    converted = converted.dropna(subset=["booking_created"])
    if converted.empty:
        return None
    start = pd.to_datetime(converted["created_at"])
    finish = pd.to_datetime(converted["booking_created"])
    days = (finish - start).dt.total_seconds().to_numpy(dtype=float) / 86400.0
    days = days[np.isfinite(days)]
    days = days[days >= 0]
    if days.size == 0:
        return None
    return round(float(np.mean(days)), 1)
