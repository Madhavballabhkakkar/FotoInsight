"""Payment tracking. Revenue elsewhere in the app reads these rows."""

from flask import Blueprint, jsonify, render_template, request, session

from app.authz import admin_required
from app.errors import AppError
from app.models import payment as payments
from app.models.booking import choices as booking_choices
from app.models.payment import summary
from app.utils import parse_page
from app.validators import payment_payload

bp = Blueprint("payments", __name__)


@bp.route("/admin/payments")
@admin_required
def payment_list():
    page, per_page = parse_page(request.args)
    rows, info = payments.list_payments(
        q=request.args.get("q", "").strip(),
        status=request.args.get("status", "").strip(),
        method=request.args.get("method", "").strip(),
        date_from=request.args.get("date_from") or None,
        date_to=request.args.get("date_to") or None,
        page=page,
        per_page=per_page,
    )
    return render_template("admin/payments/list.html", rows=rows, pagination=info, filters=request.args, summary=summary())


@bp.route("/admin/payments/new")
@admin_required
def new_payment():
    return render_template("admin/payments/form.html", payment=None, bookings=booking_choices(), selected_booking=request.args.get("booking", ""))


@bp.route("/admin/payments/<int:payment_id>/edit")
@admin_required
def edit_payment(payment_id):
    payment = payments.get(payment_id)
    if not payment:
        raise AppError("Payment not found.", 404)
    return render_template("admin/payments/form.html", payment=payment, bookings=booking_choices(), selected_booking=payment["booking_id"])


@bp.route("/api/payments", methods=["GET"])
@admin_required
def api_list():
    page, per_page = parse_page(request.args)
    rows, info = payments.list_payments(page=page, per_page=per_page, status=request.args.get("status", ""))
    return jsonify({"items": rows, "pagination": info, "summary": summary()})


@bp.route("/api/payments", methods=["POST"])
@admin_required
def api_create():
    result = payments.create(payment_payload(request.get_json(silent=True) or {}), user_id=session.get("user_id"))
    return jsonify(result), 201


@bp.route("/api/payments/<int:payment_id>", methods=["PUT"])
@admin_required
def api_update(payment_id):
    payments.update(payment_id, payment_payload(request.get_json(silent=True) or {}))
    return jsonify({"ok": True})


@bp.route("/api/payments/<int:payment_id>", methods=["DELETE"])
@admin_required
def api_delete(payment_id):
    payments.delete(payment_id)
    return jsonify({"ok": True})
