"""Admin and employee sign-in."""

from flask import Blueprint, jsonify, redirect, render_template, request, session, url_for

from app.models.user import authenticate

bp = Blueprint("auth", __name__)


def _safe_next(value):
    if value and value.startswith("/admin") and not value.startswith("//"):
        return value
    return url_for("dashboard.overview")


@bp.route("/admin/login")
def login():
    if session.get("user_id"):
        return redirect(_safe_next(request.args.get("next")))
    return render_template("auth/login.html", next_url=request.args.get("next", ""))


@bp.route("/api/auth/login", methods=["POST"])
def login_api():
    data = request.get_json(silent=True) or {}
    user = authenticate(data.get("username"), data.get("password"))
    if not user:
        return jsonify({"error": "Incorrect username or password."}), 401
    next_url = _safe_next(data.get("next"))
    session.clear()
    session.permanent = True
    session["csrf"] = __import__("secrets").token_hex(16)
    session["user_id"] = user["id"]
    session["username"] = user["username"]
    session["role"] = user["role"]
    session["employee_id"] = user["employee_id"]
    session["display_name"] = user["display_name"]
    return jsonify({"ok": True, "role": user["role"], "redirect": next_url, "csrf_token": session["csrf"]})


@bp.route("/admin/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("auth.login"))
