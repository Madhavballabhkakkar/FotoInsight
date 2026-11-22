"""Booking pages, including a month calendar."""

import calendar
from datetime import date

from flask import Blueprint, jsonify, render_template, request

from app.authz import admin_required, employee_scope, login_required
from app.errors import AppError
from app.models import booking as bookings
from app.models.customer import choices as customer_choices
from app.models.employee import active_choices
from app.models.service import list_packages, list_services
from app.utils import parse_page
from app.validators import booking_payload, choice
from app.constants import BOOKING_STATUSES

bp = Blueprint("bookings", __name__)


def _context(booking=None):
    return {
        "booking": booking,
        "customers": customer_choices(),
        "services": list_services(),
        "packages": list_packages(),
        "employees": active_choices(),
        "enquiries": bookings.unlinked_enquiries(),
    }


@bp.route("/admin/bookings")
@login_required
def booking_list():
    view = request.args.get("view", "table")
    if view == "calendar":
        today = date.today()
        raw = request.args.get("month") or f"{today.year:04d}-{today.month:02d}"
        try:
            year, month = [int(part) for part in raw.split("-")]
            if not 1 <= month <= 12:
                raise ValueError
        except ValueError as exc:
            raise AppError("Use a month like 2026-11.") from exc
        events = bookings.month_events(year, month, employee_id=employee_scope())
        by_day = {}
        for event in events:
            day = int(str(event["event_date"])[8:10])
            by_day.setdefault(day, []).append(event)
        weeks = calendar.Calendar(firstweekday=6).monthdayscalendar(year, month)
        prev_year, prev_month = (year - 1, 12) if month == 1 else (year, month - 1)
        next_year, next_month = (year + 1, 1) if month == 12 else (year, month + 1)
        return render_template(
            "admin/bookings/calendar.html",
            events=events,
            by_day=by_day,
            weeks=weeks,
            year=year,
            month=month,
            month_name=calendar.month_name[month],
            prev_month=f"{prev_year:04d}-{prev_month:02d}",
            next_month=f"{next_year:04d}-{next_month:02d}",
        )
    page, per_page = parse_page(request.args)
    rows, info = bookings.list_bookings(
        q=request.args.get("q", "").strip(),
        status=request.args.get("status", "").strip(),
        event_type=request.args.get("event_type", "").strip(),
        date_from=request.args.get("date_from") or None,
        date_to=request.args.get("date_to") or None,
        page=page,
        per_page=per_page,
        employee_id=employee_scope(),
    )
    return render_template("admin/bookings/list.html", rows=rows, pagination=info, filters=request.args)


@bp.route("/admin/bookings/new")
@admin_required
def new_booking():
    return render_template("admin/bookings/form.html", **_context())


@bp.route("/admin/bookings/<int:booking_id>")
@login_required
def booking_detail(booking_id):
    booking = bookings.get(booking_id, employee_id=employee_scope())
    if not booking:
        raise AppError("Booking not found.", 404)
    return render_template("admin/bookings/detail.html", booking=booking)


@bp.route("/admin/bookings/<int:booking_id>/edit")
@admin_required
def edit_booking(booking_id):
    booking = bookings.get(booking_id)
    if not booking:
        raise AppError("Booking not found.", 404)
    return render_template("admin/bookings/form.html", **_context(booking))


@bp.route("/api/bookings", methods=["GET"])
@login_required
def api_list():
    page, per_page = parse_page(request.args)
    rows, info = bookings.list_bookings(
        q=request.args.get("q", "").strip(),
        status=request.args.get("status", "").strip(),
        page=page,
        per_page=per_page,
        employee_id=employee_scope(),
    )
    return jsonify({"items": rows, "pagination": info})


@bp.route("/api/bookings", methods=["POST"])
@admin_required
def api_create():
    result = bookings.create(booking_payload(request.get_json(silent=True) or {}))
    return jsonify(result), 201


@bp.route("/api/bookings/<int:booking_id>", methods=["PUT"])
@admin_required
def api_update(booking_id):
    data = request.get_json(silent=True) or {}
    payload = booking_payload(data)
    if "team" not in data:
        payload.pop("team", None)
    bookings.update(booking_id, payload)
    return jsonify({"ok": True, "id": booking_id})


@bp.route("/api/bookings/<int:booking_id>/status", methods=["POST"])
@admin_required
def api_status(booking_id):
    status = choice(request.get_json(silent=True) or {}, "status", "Booking status", BOOKING_STATUSES)
    bookings.update_status(booking_id, status)
    return jsonify({"ok": True})


@bp.route("/api/bookings/<int:booking_id>", methods=["DELETE"])
@admin_required
def api_delete(booking_id):
    bookings.delete(booking_id)
    return jsonify({"ok": True})


@bp.route("/api/bookings/calendar")
@login_required
def api_calendar():
    raw = request.args.get("month", "")
    try:
        year, month = [int(part) for part in raw.split("-")]
    except ValueError as exc:
        raise AppError("Use a month like 2026-11.") from exc
    return jsonify({"events": bookings.month_events(year, month, employee_id=employee_scope())})
