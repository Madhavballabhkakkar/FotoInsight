"""Project delivery tracking."""

from flask import Blueprint, jsonify, render_template, request

from app.authz import admin_required, employee_scope, is_admin, login_required
from app.constants import EMPLOYEE_PROJECT_FIELDS, PROJECT_STATUSES
from app.errors import AppError
from app.models import project as projects
from app.models.employee import active_choices
from app.utils import parse_page
from app.validators import choice, project_payload

bp = Blueprint("projects", __name__)


@bp.route("/admin/projects")
@login_required
def project_list():
    page, per_page = parse_page(request.args)
    delayed = request.args.get("delayed") == "1"
    rows, info = projects.list_projects(
        q=request.args.get("q", "").strip(),
        status=request.args.get("status", "").strip(),
        delayed=delayed,
        page=page,
        per_page=per_page,
        employee_id=employee_scope(),
    )
    return render_template("admin/projects/list.html", rows=rows, pagination=info, filters=request.args)


@bp.route("/admin/projects/new")
@admin_required
def new_project():
    return render_template(
        "admin/projects/form.html",
        project=None,
        bookings=projects.bookings_without_project(),
        employees=active_choices(),
    )


@bp.route("/admin/projects/<int:project_id>")
@login_required
def project_detail(project_id):
    project = projects.get(project_id, employee_id=employee_scope())
    if not project:
        raise AppError("Project not found.", 404)
    return render_template("admin/projects/detail.html", project=project)


@bp.route("/admin/projects/<int:project_id>/edit")
@admin_required
def edit_project(project_id):
    project = projects.get(project_id)
    if not project:
        raise AppError("Project not found.", 404)
    return render_template(
        "admin/projects/form.html",
        project=project,
        bookings=projects.bookings_without_project() + [{
            "id": project["booking_id"],
            "booking_code": project["booking_code"],
            "event_name": project["event_name"],
            "event_date": project["event_date"],
            "customer_name": project["customer_name"],
        }],
        employees=active_choices(),
    )


@bp.route("/api/projects", methods=["POST"])
@admin_required
def api_create():
    return jsonify(projects.create(project_payload(request.get_json(silent=True) or {}))), 201


@bp.route("/api/projects/<int:project_id>", methods=["PUT"])
@login_required
def api_update(project_id):
    current = projects.get(project_id, employee_id=employee_scope())
    if not current:
        raise AppError("Project not found.", 404)
    data = request.get_json(silent=True) or {}
    if is_admin():
        projects.update(project_id, project_payload(data))
    else:
        unknown = set(data) - EMPLOYEE_PROJECT_FIELDS
        if unknown:
            raise AppError("You can update the project status and notes only.", 403)
        status = choice(data, "status", "Project status", PROJECT_STATUSES)
        projects.update(project_id, {"status": status, "notes": data.get("notes", current["notes"])}, fields=EMPLOYEE_PROJECT_FIELDS)
    return jsonify({"ok": True})


@bp.route("/api/projects/<int:project_id>", methods=["DELETE"])
@admin_required
def api_delete(project_id):
    projects.delete(project_id)
    return jsonify({"ok": True})
