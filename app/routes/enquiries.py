"""Enquiry desk: review, assign, annotate, and convert into a booking."""

from flask import Blueprint, jsonify, render_template, request

from app.authz import admin_required, employee_scope, is_admin, login_required
from app.errors import AppError
from app.models import enquiry as enquiries
from app.models.booking import create as create_booking
from app.models.employee import active_choices
from app.models.service import get_by_name, get_package, list_packages, list_services
from app.utils import as_date, parse_page
from app.validators import enquiry_payload

bp = Blueprint("enquiries", __name__)


def _form_context(enquiry=None):
    return {
        "enquiry": enquiry,
        "services": list_services(),
        "packages": list_packages(),
        "employees": active_choices(),
        "event_types": enquiries.event_types(),
    }


@bp.route("/admin/enquiries")
@login_required
def enquiry_list():
    page, per_page = parse_page(request.args)
    rows, info = enquiries.list_enquiries(
        q=request.args.get("q", "").strip(),
        event_type=request.args.get("event_type", "").strip(),
        status=request.args.get("status", "").strip(),
        date_from=request.args.get("date_from") or None,
        date_to=request.args.get("date_to") or None,
        page=page,
        per_page=per_page,
        employee_id=employee_scope(),
    )
    return render_template("admin/enquiries/list.html", rows=rows, pagination=info, filters=request.args, event_types=enquiries.event_types())


@bp.route("/admin/enquiries/new")
@admin_required
def new_enquiry():
    return render_template("admin/enquiries/form.html", **_form_context())


@bp.route("/admin/enquiries/<int:enquiry_id>")
@login_required
def enquiry_detail(enquiry_id):
    enquiry = enquiries.get(enquiry_id, employee_id=employee_scope())
    if not enquiry:
        raise AppError("Enquiry not found.", 404)
    return render_template(
        "admin/enquiries/detail.html",
        enquiry=enquiry,
        notes=enquiries.notes(enquiry_id),
        employees=active_choices(),
        services=list_services(active_only=True),
        packages=list_packages(active_only=True),
    )


@bp.route("/admin/enquiries/<int:enquiry_id>/edit")
@login_required
def edit_enquiry(enquiry_id):
    enquiry = enquiries.get(enquiry_id, employee_id=employee_scope())
    if not enquiry:
        raise AppError("Enquiry not found.", 404)
    return render_template("admin/enquiries/form.html", **_form_context(enquiry))


@bp.route("/api/enquiries", methods=["GET"])
@login_required
def api_list():
    page, per_page = parse_page(request.args)
    rows, info = enquiries.list_enquiries(
        q=request.args.get("q", "").strip(),
        event_type=request.args.get("event_type", "").strip(),
        status=request.args.get("status", "").strip(),
        date_from=request.args.get("date_from") or None,
        date_to=request.args.get("date_to") or None,
        page=page,
        per_page=per_page,
        employee_id=employee_scope(),
    )
    return jsonify({"items": rows, "pagination": info})


@bp.route("/api/enquiries", methods=["POST"])
@admin_required
def api_create():
    data = request.get_json(silent=True) or {}
    payload = enquiry_payload(data, source="admin")
    result = enquiries.create(payload)
    return jsonify(result), 201


@bp.route("/api/enquiries/<int:enquiry_id>", methods=["PUT"])
@login_required
def api_update(enquiry_id):
    current = enquiries.get(enquiry_id, employee_id=employee_scope())
    if not current:
        raise AppError("Enquiry not found.", 404)
    data = request.get_json(silent=True) or {}
    if not is_admin():
        data = {
            "full_name": current["full_name"],
            "email": current["email"],
            "phone": current["phone"],
            "event_type": current["event_type"],
            "event_date": current["event_date"],
            "event_location": current["event_location"],
            "city": current["city"],
            "guest_count": current["guest_count"],
            "package_id": current["package_id"],
            "estimated_budget": current["estimated_budget"],
            "requirements": data.get("requirements", current["requirements"]),
            "status": data.get("status") or current["status"],
            "assigned_employee_id": current["assigned_employee_id"],
        }
    payload = enquiry_payload(data, source="admin")
    if not is_admin():
        payload["assigned_employee_id"] = current["assigned_employee_id"]
    enquiries.update(enquiry_id, payload, employee_id=employee_scope())
    return jsonify({"ok": True})


@bp.route("/api/enquiries/<int:enquiry_id>", methods=["DELETE"])
@admin_required
def api_delete(enquiry_id):
    enquiries.delete(enquiry_id)
    return jsonify({"ok": True})


@bp.route("/api/enquiries/<int:enquiry_id>/assign", methods=["POST"])
@admin_required
def api_assign(enquiry_id):
    raw = (request.get_json(silent=True) or {}).get("employee_id")
    employee_id = int(raw) if str(raw).isdigit() else None
    enquiries.assign(enquiry_id, employee_id)
    return jsonify({"ok": True})


@bp.route("/api/enquiries/<int:enquiry_id>/notes", methods=["POST"])
@login_required
def api_note(enquiry_id):
    from flask import session
    note = (request.get_json(silent=True) or {}).get("note")
    enquiries.add_note(enquiry_id, session["user_id"], note, employee_id=employee_scope())
    return jsonify({"ok": True})


@bp.route("/api/enquiries/<int:enquiry_id>/convert", methods=["POST"])
@admin_required
def api_convert(enquiry_id):
    enquiry = enquiries.get(enquiry_id)
    if not enquiry:
        raise AppError("Enquiry not found.", 404)
    data = request.get_json(silent=True) or {}
    service = None
    if str(data.get("service_id") or "").isdigit():
        service_id = int(data["service_id"])
    else:
        service = get_by_name(enquiry["event_type"])
        if not service:
            raise AppError("Choose a service before converting this enquiry.")
        service_id = service["id"]
    package_id = enquiry["package_id"]
    if str(data.get("package_id") or "").isdigit():
        package_id = int(data["package_id"])
    if data.get("total_amount") not in (None, ""):
        total = data.get("total_amount")
    elif package_id:
        package = get_package(package_id)
        total = package["price"] if package else None
    elif enquiry["estimated_budget"]:
        total = enquiry["estimated_budget"]
    else:
        service = service or get_by_name(enquiry["event_type"])
        total = service["base_price"] if service else None
    if total in (None, ""):
        raise AppError("Set a price before converting this enquiry.")
    if not enquiry["customer_id"]:
        from app.models.customer import create as create_customer
        from app.db import query_one
        found = query_one("SELECT id FROM customers WHERE email=%s ORDER BY id DESC LIMIT 1", (enquiry["email"],))
        customer_id = found["id"] if found else create_customer({
            "full_name": enquiry["full_name"],
            "email": enquiry["email"],
            "phone": enquiry["phone"],
            "city": enquiry["city"] or "Unknown",
            "address": None,
            "registration_date": __import__("datetime").date.today(),
        }, is_demo=enquiry["is_demo"])
    else:
        customer_id = enquiry["customer_id"]
    event_date = as_date(data.get("event_date")) if data.get("event_date") else as_date(enquiry["event_date"])
    if not event_date:
        raise AppError("An event date is required to create a booking.")
    result = create_booking({
        "customer_id": customer_id,
        "service_id": service_id,
        "package_id": package_id,
        "enquiry_id": enquiry_id,
        "event_name": data.get("event_name") or f"{enquiry['event_type']} — {enquiry['full_name']}",
        "event_date": event_date,
        "event_location": data.get("event_location") or enquiry["event_location"] or enquiry["city"] or "Studio",
        "city": data.get("city") or enquiry["city"] or "Unknown",
        "total_amount": total,
        "status": "confirmed",
        "notes": enquiry["requirements"],
        "team": [],
    }, is_demo=enquiry["is_demo"])
    return jsonify(result), 201
