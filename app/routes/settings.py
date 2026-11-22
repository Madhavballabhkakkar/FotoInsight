"""Studio details, staff records, and the signed-in user's password."""

from flask import Blueprint, jsonify, render_template, request, session

from app.authz import admin_required, login_required
from app.errors import AppError
from app.models import settings as settings_model
from app.models.employee import create as create_employee, get as get_employee, list_employees, update as update_employee
from app.models.user import authenticate, by_employee, create_login, set_password
from app.validators import employee_payload, password_pair, require_text, settings_payload

bp = Blueprint("settings", __name__)


@bp.route("/admin/settings")
@admin_required
def settings_page():
    employees = []
    for employee in list_employees():
        login = by_employee(employee["id"])
        employee["login"] = login
        employees.append(employee)
    return render_template("admin/settings.html", settings=settings_model.get(), employees=employees)


@bp.route("/api/settings", methods=["PUT"])
@admin_required
def update_settings():
    settings_model.update(settings_payload(request.get_json(silent=True) or {}))
    return jsonify({"ok": True})


@bp.route("/api/employees", methods=["POST"])
@admin_required
def api_create_employee():
    new_id = create_employee(employee_payload(request.get_json(silent=True) or {}))
    return jsonify({"id": new_id}), 201


@bp.route("/api/employees/<int:employee_id>", methods=["PUT"])
@admin_required
def api_update_employee(employee_id):
    update_employee(employee_id, employee_payload(request.get_json(silent=True) or {}))
    return jsonify({"ok": True})


@bp.route("/api/employees/<int:employee_id>/login", methods=["POST"])
@admin_required
def api_employee_login(employee_id):
    employee = get_employee(employee_id)
    if not employee:
        raise AppError("Employee not found.", 404)
    data = request.get_json(silent=True) or {}
    username = require_text(data, "username", "Username", 80)
    password = password_pair(data.get("password"))
    role = data.get("role") or "employee"
    if role not in ("admin", "employee"):
        raise AppError("Role must be admin or employee.")
    user_id = create_login(employee, username, password, role)
    return jsonify({"id": user_id}), 201


@bp.route("/api/account/password", methods=["POST"])
@login_required
def change_password():
    data = request.get_json(silent=True) or {}
    user = authenticate(session.get("username"), data.get("current_password"))
    if not user or user["id"] != session.get("user_id"):
        raise AppError("The current password is incorrect.")
    set_password(session["user_id"], password_pair(data.get("new_password")))
    return jsonify({"ok": True, "message": "Password updated."})
