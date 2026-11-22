"""Pages anyone can open, plus the public enquiry and contact forms."""

from flask import Blueprint, jsonify, redirect, render_template, request, url_for

from app.models.customer import public_feedback
from app.models.employee import list_employees
from app.models.enquiry import create as create_enquiry
from app.models.service import list_packages, list_services
from app.portfolio import CATEGORIES, ITEMS
from app.validators import contact_payload, enquiry_payload

bp = Blueprint("public", __name__)


@bp.route("/")
def home():
    services = [service for service in list_services(active_only=True)][:6]
    return render_template("public/home.html", services=services, feedback=public_feedback(), portfolio=ITEMS[:8])


@bp.route("/about")
def about():
    return render_template("public/about.html", team=list_employees(include_inactive=False), service_count=len(list_services(active_only=True)))


@bp.route("/services")
def services():
    return render_template("public/services.html", services=list_services(active_only=True))


@bp.route("/portfolio")
def portfolio():
    return render_template("public/portfolio.html", items=ITEMS, categories=CATEGORIES)


@bp.route("/enquiry", methods=["GET", "POST"])
def enquiry():
    services = list_services(active_only=True)
    packages = list_packages(active_only=True)
    if request.method == "POST" and not request.is_json:
        try:
            result = create_enquiry(enquiry_payload(request.form, source="website"))
        except Exception as exc:
            from app.errors import AppError
            message = exc.message if isinstance(exc, AppError) else "The enquiry could not be saved."
            return render_template(
                "public/enquiry.html",
                services=services,
                packages=packages,
                error=message,
                selected_service=request.form.get("event_type", ""),
            ), 400
        return redirect(url_for("public.enquiry", submitted=result["enquiry_code"]))
    return render_template(
        "public/enquiry.html",
        services=services,
        packages=packages,
        selected_service=request.args.get("service", ""),
        selected_package=request.args.get("package", ""),
        submitted=request.args.get("submitted"),
    )


@bp.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST" and not request.is_json:
        try:
            result = create_enquiry(contact_payload(request.form))
        except Exception as exc:
            from app.errors import AppError
            message = exc.message if isinstance(exc, AppError) else "The message could not be saved."
            return render_template("public/contact.html", error=message), 400
        return redirect(url_for("public.contact", submitted=result["enquiry_code"]))
    return render_template("public/contact.html", submitted=request.args.get("submitted"))


@bp.route("/api/public/enquiries", methods=["POST"])
def api_enquiry():
    payload = request.get_json(silent=True) or {}
    result = create_enquiry(enquiry_payload(payload, source="website"))
    status = 200 if result["duplicate"] else 201
    return jsonify({
        "ok": True,
        "duplicate": result["duplicate"],
        "enquiry_code": result["enquiry_code"],
        "message": "This enquiry was already received." if result["duplicate"] else "Your enquiry has been received.",
    }), status


@bp.route("/api/public/contact", methods=["POST"])
def api_contact():
    payload = request.get_json(silent=True) or {}
    result = create_enquiry(contact_payload(payload))
    status = 200 if result["duplicate"] else 201
    return jsonify({
        "ok": True,
        "duplicate": result["duplicate"],
        "enquiry_code": result["enquiry_code"],
        "message": "This message was already received." if result["duplicate"] else "Your message has been received.",
    }), status


@bp.route("/health")
def health():
    from app.db import query_one
    try:
        query_one("SELECT 1 AS ok")
    except Exception:
        return jsonify({"ok": False, "database": "down"}), 500
    return jsonify({"ok": True, "database": "up"})
