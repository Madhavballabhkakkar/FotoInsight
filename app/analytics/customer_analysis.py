"""Customer counts, spending, and simple rule-based segments."""

import numpy as np
import pandas as pd

from app.analytics.loader import customers as load_customers
from app.analytics.loader import dataframe
from app.utils import month_keys, round_money


def analyse(start, end):
    everyone = load_customers(registered_through=end)
    labels = month_keys(start, end)
    empty_growth = {"labels": labels, "values": [0 for _ in labels]}
    if everyone.empty:
        return {
            "total_customers": 0,
            "new_customers": 0,
            "returning_customers": 0,
            "average_spending": None,
            "location": {"labels": [], "values": []},
            "growth": empty_growth,
            "high_value": [],
            "high_value_threshold": None,
            "segments": [],
            "segment_note": "Not enough customers in this range to build segments.",
            "has_data": False,
        }

    registration = pd.to_datetime(everyone["registration_date"])
    start_ts = pd.Timestamp(start)
    end_ts = pd.Timestamp(end)
    in_period = (registration >= start_ts) & (registration <= end_ts)
    new_customers = int(np.sum(in_period.to_numpy()))

    active_ids = _customers_with_bookings_in_range(start, end)
    returning_mask = everyone["id"].isin(active_ids) & (everyone["booking_count"] >= 2)
    returning = int(np.sum(returning_mask.to_numpy()))

    period_spending = _spending_in_range(start, end)
    if period_spending:
        average = round_money(float(np.mean(np.array(list(period_spending.values()), dtype=float))))
    else:
        average = None

    cohort = everyone.loc[in_period].copy()
    if cohort.empty:
        location = {"labels": [], "values": []}
    else:
        counts = cohort["city"].fillna("Unknown").value_counts()
        location = {"labels": [str(item) for item in counts.index.tolist()], "values": [int(item) for item in counts.to_numpy()]}

    growth_values = []
    if cohort.empty:
        growth_values = [0 for _ in labels]
    else:
        cohort["month"] = pd.to_datetime(cohort["registration_date"]).dt.strftime("%Y-%m")
        grouped = cohort.groupby("month")["id"].count()
        growth_values = [int(grouped.get(label, 0)) for label in labels]

    spenders = everyone[everyone["spending"] > 0].copy()
    high_value = []
    threshold = None
    if len(spenders) >= 4:
        threshold = float(np.percentile(spenders["spending"].to_numpy(dtype=float), 75))
        picked = spenders[spenders["spending"] >= threshold].sort_values("spending", ascending=False).head(8)
        for _, row in picked.iterrows():
            high_value.append({
                "id": int(row["id"]),
                "name": row["full_name"],
                "city": row["city"],
                "spending": round_money(row["spending"]),
                "bookings": int(row["booking_count"]),
            })
    elif len(spenders) > 0:
        threshold = None

    segments = _segments(everyone, in_period.to_numpy(), threshold)
    return {
        "total_customers": int(everyone.shape[0]),
        "new_customers": new_customers,
        "returning_customers": returning,
        "average_spending": average,
        "location": location,
        "growth": {"labels": labels, "values": growth_values},
        "high_value": high_value,
        "high_value_threshold": round_money(threshold) if threshold is not None else None,
        "segments": segments,
        "segment_note": (
            "Segments use plain business rules, not a black-box model. "
            "A person can match more than one rule. High-value uses lifetime collected spend. "
            "Returning in this table means two or more bookings on record. "
            "The Returning card counts only people who also booked during the selected dates."
        ),
        "has_data": True,
    }


def _customers_with_bookings_in_range(start, end):
    frame = dataframe(
        """
        SELECT DISTINCT customer_id
        FROM bookings
        WHERE DATE(created_at) >= %s AND DATE(created_at) <= %s AND status <> 'cancelled'
        """,
        (start, end),
    )
    if frame.empty:
        return set()
    return set(int(value) for value in frame["customer_id"].tolist())


def _spending_in_range(start, end):
    frame = dataframe(
        """
        SELECT b.customer_id,
               SUM(CASE
                   WHEN p.status IN ('paid','partially_paid') THEN p.amount
                   WHEN p.status = 'refunded' THEN -p.amount
                   ELSE 0 END) AS spending
        FROM payments p
        JOIN bookings b ON b.id = p.booking_id
        WHERE p.payment_date >= %s AND p.payment_date <= %s
        GROUP BY b.customer_id
        """,
        (start, end),
        numbers=("spending",),
    )
    if frame.empty:
        return {}
    return {int(row.customer_id): float(row.spending) for row in frame.itertuples(index=False) if row.spending > 0}


def _segments(everyone, in_period_mask, threshold):
    bookings = everyone["booking_count"].to_numpy(dtype=float)
    spending = everyone["spending"].to_numpy(dtype=float)
    rules = [
        (
            "High-value",
            "Lifetime collected spend is at or above the 75th percentile of paying customers.",
            (spending >= threshold) if threshold is not None else np.zeros(len(everyone), dtype=bool),
        ),
        (
            "Returning",
            "Two or more bookings on record.",
            bookings >= 2,
        ),
        (
            "New",
            "Registered during the selected dates and fewer than two bookings.",
            in_period_mask & (bookings < 2),
        ),
        (
            "One-time",
            "Exactly one booking, and not in the high-value group.",
            (bookings == 1) & ~((spending >= threshold) if threshold is not None else np.zeros(len(everyone), dtype=bool)),
        ),
        (
            "Prospect",
            "Registered, but no booking yet.",
            bookings == 0,
        ),
    ]
    segments = []
    for name, rule, mask in rules:
        segments.append({"name": name, "rule": rule, "count": int(np.sum(mask))})
    if threshold is None:
        segments[0]["count"] = 0
        segments[0]["rule"] += " Not shown until at least four paying customers exist."
    return segments
