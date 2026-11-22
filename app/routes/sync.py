"""Admin page for compulsory local files and Firebase cloud sync."""

from flask import Blueprint, current_app, jsonify, render_template, request

from app.authz import admin_required
from app.firebase_sync import configured, pull_summary, push_all
from app.local_store import DATA_DIR, export_all, list_local_files

bp = Blueprint("sync", __name__)


@bp.route("/admin/sync")
@admin_required
def sync_page():
    return render_template(
        "admin/sync.html",
        files=list_local_files(),
        data_folder=str(DATA_DIR),
        firebase_ready=configured(),
        firebase_url=current_app.config.get("FIREBASE_DB_URL") or "",
    )


@bp.route("/api/sync/local", methods=["POST"])
@admin_required
def api_export_local():
    result = export_all()
    return jsonify(result)


@bp.route("/api/sync/firebase", methods=["POST"])
@admin_required
def api_push_firebase():
    result = push_all()
    return jsonify(result)


@bp.route("/api/sync/firebase", methods=["GET"])
@admin_required
def api_pull_firebase():
    return jsonify(pull_summary())


@bp.route("/api/sync/files")
@admin_required
def api_list_files():
    return jsonify({"files": list_local_files(), "folder": str(DATA_DIR)})
