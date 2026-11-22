"""Services and packages. Public prices come from these records."""

from pathlib import Path

from flask import Blueprint, current_app, jsonify, render_template, request

from app.authz import admin_required
from app.errors import AppError
from app.models import service as services
from app.validators import package_payload, service_payload

bp = Blueprint("services", __name__)


@bp.route("/admin/services")
@admin_required
def service_list():
    return render_template("admin/services/list.html", services=services.list_services(), packages=services.list_packages())


@bp.route("/admin/services/new")
@admin_required
def new_service():
    return render_template("admin/services/form.html", service=None)


@bp.route("/admin/services/<int:service_id>/edit")
@admin_required
def edit_service(service_id):
    service = services.get(service_id)
    if not service:
        raise AppError("Service not found.", 404)
    return render_template("admin/services/form.html", service=service)


@bp.route("/admin/packages/new")
@admin_required
def new_package():
    return render_template("admin/services/package_form.html", package=None, services=services.list_services())


@bp.route("/admin/packages/<int:package_id>/edit")
@admin_required
def edit_package(package_id):
    package = services.get_package(package_id)
    if not package:
        raise AppError("Package not found.", 404)
    return render_template("admin/services/package_form.html", package=package, services=services.list_services())


@bp.route("/api/services", methods=["POST"])
@admin_required
def api_create_service():
    new_id = services.create(service_payload(request.get_json(silent=True) or {}))
    return jsonify({"id": new_id}), 201


@bp.route("/api/services/<int:service_id>", methods=["PUT"])
@admin_required
def api_update_service(service_id):
    services.update(service_id, service_payload(request.get_json(silent=True) or {}))
    return jsonify({"ok": True})


@bp.route("/api/services/<int:service_id>", methods=["DELETE"])
@admin_required
def api_delete_service(service_id):
    services.delete(service_id)
    return jsonify({"ok": True})


@bp.route("/api/services/<int:service_id>/status", methods=["POST"])
@admin_required
def api_status(service_id):
    status = (request.get_json(silent=True) or {}).get("status")
    services.set_status(service_id, status)
    return jsonify({"ok": True})


@bp.route("/api/services/<int:service_id>/image", methods=["POST"])
@admin_required
def api_image(service_id):
    upload = request.files.get("image")
    if not upload or not upload.filename:
        raise AppError("Choose an image to upload.")
    data = upload.read()
    kind = _sniff(data)
    if not kind:
        raise AppError("Upload a JPG, PNG, or WebP image.")
    folder = Path(current_app.static_folder) / "uploads"
    folder.mkdir(parents=True, exist_ok=True)
    filename = f"service_{service_id}.{kind}"
    (folder / filename).write_bytes(data)
    services.set_image(service_id, f"uploads/{filename}")
    return jsonify({"ok": True, "image_path": f"uploads/{filename}"})


@bp.route("/api/packages", methods=["POST"])
@admin_required
def api_create_package():
    new_id = services.create_package(package_payload(request.get_json(silent=True) or {}))
    return jsonify({"id": new_id}), 201


@bp.route("/api/packages/<int:package_id>", methods=["PUT"])
@admin_required
def api_update_package(package_id):
    services.update_package(package_id, package_payload(request.get_json(silent=True) or {}))
    return jsonify({"ok": True})


@bp.route("/api/packages/<int:package_id>", methods=["DELETE"])
@admin_required
def api_delete_package(package_id):
    services.delete_package(package_id)
    return jsonify({"ok": True})


def _sniff(data):
    if data.startswith(b"\xff\xd8\xff"):
        return "jpg"
    if data.startswith(b"\x89PNG\r\n\x1a\n"):
        return "png"
    if len(data) > 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "webp"
    return None
