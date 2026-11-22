"""Customer pages and the customer API."""

from flask import Blueprint, jsonify, render_template, request

from app.authz import admin_required, employee_scope, login_required
from app.errors import AppError
from app.models import customer as customers
from app.utils import code_for, parse_page
from app.validators import customer_payload

bp = Blueprint("customers", __name__)


@bp.route("/admin/customers")
@login_required
def customer_list():
    page, per_page = parse_page(request.args)
    scope = employee_scope()
    rows, info = customers.list_customers(
        q=request.args.get("q", "").strip(),
        city=request.args.get("city", "").strip(),
        sort=request.args.get("sort", "newest"),
        page=page,
        per_page=per_page,
        employee_id=scope,
    )
    return render_template(
        "admin/customers/list.html",
        rows=rows,
        pagination=info,
        cities=customers.cities(scope),
        filters=request.args,
    )


@bp.route("/admin/customers/new")
@admin_required
def new_customer():
    return render_template("admin/customers/form.html", customer=None)


@bp.route("/admin/customers/<int:customer_id>")
@login_required
def customer_detail(customer_id):
    customer = customers.get(customer_id, employee_id=employee_scope())
    if not customer:
        raise AppError("Customer not found.", 404)
    return render_template("admin/customers/detail.html", customer=customer, history=customers.history(customer_id), code=code_for("CUS", customer_id))


@bp.route("/admin/customers/<int:customer_id>/edit")
@login_required
def edit_customer(customer_id):
    customer = customers.get(customer_id, employee_id=employee_scope())
    if not customer:
        raise AppError("Customer not found.", 404)
    return render_template("admin/customers/form.html", customer=customer)


@bp.route("/api/customers", methods=["GET"])
@login_required
def api_list():
    page, per_page = parse_page(request.args)
    rows, info = customers.list_customers(
        q=request.args.get("q", "").strip(),
        city=request.args.get("city", "").strip(),
        sort=request.args.get("sort", "newest"),
        page=page,
        per_page=per_page,
        employee_id=employee_scope(),
    )
    return jsonify({"items": rows, "pagination": info})


@bp.route("/api/customers", methods=["POST"])
@admin_required
def api_create():
    payload = customer_payload(request.get_json(silent=True) or {})
    new_id = customers.create(payload)
    return jsonify({"id": new_id, "customer_code": code_for("CUS", new_id)}), 201


@bp.route("/api/customers/<int:customer_id>", methods=["GET"])
@login_required
def api_get(customer_id):
    customer = customers.get(customer_id, employee_id=employee_scope())
    if not customer:
        raise AppError("Customer not found.", 404)
    customer["history"] = customers.history(customer_id)
    customer["customer_code"] = code_for("CUS", customer_id)
    return jsonify(customer)


@bp.route("/api/customers/<int:customer_id>", methods=["PUT"])
@login_required
def api_update(customer_id):
    if not customers.get(customer_id, employee_id=employee_scope()):
        raise AppError("Customer not found.", 404)
    customers.update(customer_id, customer_payload(request.get_json(silent=True) or {}), employee_id=employee_scope())
    return jsonify({"ok": True, "id": customer_id})


@bp.route("/api/customers/<int:customer_id>", methods=["DELETE"])
@admin_required
def api_delete(customer_id):
    customers.delete(customer_id)
    return jsonify({"ok": True})
