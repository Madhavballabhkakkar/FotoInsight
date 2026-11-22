"""Download a report as PDF, Excel, or CSV."""

from flask import Blueprint, jsonify, render_template, request, send_file
import io

from app.analytics.ranges import PRESETS, resolve_range
from app.authz import admin_required
from app.errors import AppError
from app.reports.generators import REPORTS, generate

bp = Blueprint("reports", __name__)


@bp.route("/admin/reports")
@admin_required
def reports_page():
    return render_template("admin/reports.html", presets=PRESETS, reports=REPORTS)


@bp.route("/api/reports/<report_key>")
@admin_required
def download(report_key):
    if report_key not in REPORTS:
        raise AppError("That report does not exist.", 404)
    file_format = request.args.get("format", "pdf")
    if file_format not in ("pdf", "xlsx", "csv"):
        raise AppError("Choose pdf, xlsx, or csv.")
    window = resolve_range(request.args.get("preset"), request.args.get("start"), request.args.get("end"))
    payload, mime, filename = generate(report_key, window["start"], window["end"], file_format)
    return send_file(io.BytesIO(payload), mimetype=mime, as_attachment=True, download_name=filename)


@bp.route("/api/reports")
@admin_required
def report_index():
    return jsonify({"reports": [{"key": key, "title": title} for key, title in REPORTS.items()]})
