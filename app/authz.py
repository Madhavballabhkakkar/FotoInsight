"""Who can open a page. Admin sees the whole studio. An employee sees assigned work."""

from functools import wraps

from flask import jsonify, redirect, request, session, url_for

from app.errors import AppError


def current_user():
    if "user_id" not in session:
        return None
    return {
        "id": session["user_id"],
        "username": session.get("username"),
        "role": session.get("role"),
        "employee_id": session.get("employee_id"),
        "display_name": session.get("display_name"),
    }


def is_admin():
    return session.get("role") == "admin"


def employee_scope():
    """None for admins (no filter). The employee id for everyone else."""
    if session.get("role") == "employee":
        return session.get("employee_id")
    return None


def wants_json():
    return request.path.startswith("/api/") or request.is_json or request.headers.get("X-Requested-With") == "fetch"


def login_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            if wants_json():
                return jsonify({"error": "Authentication required."}), 401
            return redirect(url_for("auth.login", next=request.path))
        return view(*args, **kwargs)
    return wrapper


def admin_required(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if "user_id" not in session:
            if wants_json():
                return jsonify({"error": "Authentication required."}), 401
            return redirect(url_for("auth.login", next=request.path))
        if session.get("role") != "admin":
            if wants_json():
                return jsonify({"error": "You do not have permission for this action."}), 403
            raise AppError("You do not have permission to open that page.", 403)
        return view(*args, **kwargs)
    return wrapper
