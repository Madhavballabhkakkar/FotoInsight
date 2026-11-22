"""Overview screen, global search, and the chart data behind the KPI cards."""

from datetime import date

from flask import Blueprint, jsonify, render_template, request

from app.analytics.overview import build as build_overview
from app.analytics.ranges import PRESETS, resolve_range
from app.authz import employee_scope
from app.db import query_all
from app.utils import clean_rows, like

bp = Blueprint("dashboard", __name__)


@bp.route("/admin/")
@bp.route("/admin")
def overview():
    return render_template("admin/overview.html", presets=PRESETS, today=date.today().isoformat())


@bp.route("/api/dashboard")
def overview_api():
    window = resolve_range(request.args.get("preset"), request.args.get("start"), request.args.get("end"))
    payload = build_overview(window["start"], window["end"], employee_id=employee_scope())
    payload["range"] = {"preset": window["preset"], "label": window["label"], "start": window["start"].isoformat(), "end": window["end"].isoformat()}
    return jsonify(payload)


@bp.route("/admin/search")
def search_page():
    term = request.args.get("q", "").strip()
    return render_template("admin/search.html", q=term, results=search_records(term, employee_scope()) if term else [])


@bp.route("/api/search")
def search_api():
    term = request.args.get("q", "").strip()
    return jsonify({"results": search_records(term, employee_scope())})


def search_records(term, employee_id=None):
    if len(term) < 2:
        return []
    pattern = like(term)
    results = []
    customer_sql = """
        SELECT id, full_name, email, city FROM customers c
        WHERE (full_name LIKE %s ESCAPE '\\\\' OR email LIKE %s ESCAPE '\\\\' OR phone LIKE %s ESCAPE '\\\\')
    """
    params = [pattern, pattern, pattern]
    if employee_id:
        customer_sql += """
            AND (
                id IN (SELECT customer_id FROM enquiries WHERE assigned_employee_id=%s AND customer_id IS NOT NULL)
                OR id IN (
                    SELECT b.customer_id FROM bookings b
                    JOIN booking_team bt ON bt.booking_id=b.id WHERE bt.employee_id=%s
                )
            )
        """
        params.extend([employee_id, employee_id])
    customer_sql += " ORDER BY full_name LIMIT 8"
    for row in clean_rows(query_all(customer_sql, params)):
        results.append({"type": "Customer", "label": row["full_name"], "meta": row["city"], "url": f"/admin/customers/{row['id']}"})

    enquiry_sql = """
        SELECT id, enquiry_code, full_name, event_type FROM enquiries
        WHERE (full_name LIKE %s ESCAPE '\\\\' OR enquiry_code LIKE %s ESCAPE '\\\\' OR phone LIKE %s ESCAPE '\\\\')
    """
    enquiry_params = [pattern, pattern, pattern]
    if employee_id:
        enquiry_sql += " AND assigned_employee_id=%s"
        enquiry_params.append(employee_id)
    enquiry_sql += " ORDER BY created_at DESC LIMIT 8"
    for row in clean_rows(query_all(enquiry_sql, enquiry_params)):
        results.append({"type": "Enquiry", "label": f"{row['enquiry_code']} · {row['full_name']}", "meta": row["event_type"], "url": f"/admin/enquiries/{row['id']}"})

    booking_sql = """
        SELECT b.id, b.booking_code, b.event_name, c.full_name
        FROM bookings b JOIN customers c ON c.id=b.customer_id
        WHERE (b.booking_code LIKE %s ESCAPE '\\\\' OR b.event_name LIKE %s ESCAPE '\\\\' OR c.full_name LIKE %s ESCAPE '\\\\')
    """
    booking_params = [pattern, pattern, pattern]
    if employee_id:
        booking_sql += " AND EXISTS (SELECT 1 FROM booking_team bt WHERE bt.booking_id=b.id AND bt.employee_id=%s)"
        booking_params.append(employee_id)
    booking_sql += " ORDER BY b.event_date DESC LIMIT 8"
    for row in clean_rows(query_all(booking_sql, booking_params)):
        results.append({"type": "Booking", "label": f"{row['booking_code']} · {row['event_name']}", "meta": row["full_name"], "url": f"/admin/bookings/{row['id']}"})
    return results
