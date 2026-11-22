"""Turn a filter name such as "Last 30 days" into a real start and end date."""

import calendar
from datetime import date, timedelta

from app.errors import AppError
from app.utils import as_date

PRESETS = [
    ("7d", "Last 7 days"),
    ("30d", "Last 30 days"),
    ("3m", "Last 3 months"),
    ("6m", "Last 6 months"),
    ("this_year", "This year"),
    ("custom", "Custom range"),
]
PRESET_LABELS = dict(PRESETS)


def _add_months(day, months):
    month_index = day.month - 1 + months
    year = day.year + month_index // 12
    month = month_index % 12 + 1
    last_day = calendar.monthrange(year, month)[1]
    return date(year, month, min(day.day, last_day))


def resolve_range(preset, start_text=None, end_text=None):
    today = date.today()
    preset = preset or "this_year"
    if preset == "7d":
        start, end = today - timedelta(days=6), today
    elif preset == "30d":
        start, end = today - timedelta(days=29), today
    elif preset == "3m":
        start, end = _add_months(today, -3), today
    elif preset == "6m":
        start, end = _add_months(today, -6), today
    elif preset == "this_year":
        start, end = date(today.year, 1, 1), today
    elif preset == "custom":
        if not start_text or not end_text:
            raise AppError("Choose both a start date and an end date.")
        start = as_date(start_text)
        end = as_date(end_text)
        if start > end:
            raise AppError("The start date must be on or before the end date.")
        if (end - start).days > 3660:
            raise AppError("Choose a range shorter than 10 years.")
    else:
        raise AppError("That date filter is not recognised.")
    return {
        "preset": preset,
        "label": PRESET_LABELS.get(preset, preset),
        "start": start,
        "end": end,
    }


def previous_period(start, end):
    days = (end - start).days + 1
    prev_end = start - timedelta(days=1)
    prev_start = prev_end - timedelta(days=days - 1)
    return prev_start, prev_end
