"""Analytics page. The maths lives in app.analytics, not in this file."""

from flask import Blueprint, jsonify, render_template, request

from app.analytics.customer_analysis import analyse as analyse_customers
from app.analytics.enquiry_analysis import analyse as analyse_enquiries
from app.analytics.forecast import build as build_forecast
from app.analytics.insights import build as build_insights
from app.analytics.location import analyse as analyse_locations
from app.analytics.ranges import PRESETS, resolve_range
from app.analytics.revenue import analyse as analyse_revenue
from app.analytics.seasonal import analyse as analyse_seasonal
from app.analytics.service_analysis import analyse as analyse_services
from app.authz import admin_required

bp = Blueprint("analytics", __name__)


@bp.route("/admin/analytics")
@admin_required
def analytics_page():
    return render_template("admin/analytics.html", presets=PRESETS)


@bp.route("/api/analytics")
@admin_required
def analytics_api():
    window = resolve_range(request.args.get("preset"), request.args.get("start"), request.args.get("end"))
    start, end = window["start"], window["end"]
    revenue = analyse_revenue(start, end)
    customers = analyse_customers(start, end)
    enquiries = analyse_enquiries(start, end)
    services = analyse_services(start, end)
    seasonal = analyse_seasonal(start, end)
    locations = analyse_locations(start, end)
    return jsonify({
        "range": {"preset": window["preset"], "label": window["label"], "start": start.isoformat(), "end": end.isoformat()},
        "revenue": revenue,
        "customers": customers,
        "enquiries": enquiries,
        "services": services,
        "seasonal": seasonal,
        "locations": locations,
        "insights": build_insights(start, end, revenue, customers, enquiries, services, seasonal, locations),
        "forecast": build_forecast(),
    })
