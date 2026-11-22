"""FotoInsight application factory."""

import os
import secrets

from flask import Flask, jsonify, redirect, render_template, request, session, url_for
from flask.json.provider import DefaultJSONProvider
from pymysql.err import IntegrityError, OperationalError
from werkzeug.exceptions import RequestEntityTooLarge

from app.config import Config, ProductionConfig
from app.db import close_db, query_one
from app.errors import AppError


class AppJSONProvider(DefaultJSONProvider):
    def default(self, value):
        from datetime import date, datetime
        from decimal import Decimal

        if isinstance(value, Decimal):
            return float(value)
        if isinstance(value, datetime):
            return value.strftime("%Y-%m-%d %H:%M:%S")
        if isinstance(value, date):
            return value.isoformat()
        return super().default(value)


def create_app(config_object=None):
    app = Flask(__name__, template_folder="templates", static_folder="static")
    if config_object is None:
        config_object = ProductionConfig if os.environ.get("APP_ENV") == "production" else Config
    app.config.from_object(config_object)
    app.json = AppJSONProvider(app)
    app.teardown_appcontext(close_db)

    @app.before_request
    def prepare_csrf():
        if "csrf" not in session:
            session["csrf"] = secrets.token_hex(16)

    @app.before_request
    def check_csrf():
        if request.method not in ("POST", "PUT", "PATCH", "DELETE"):
            return None
        sent = request.headers.get("X-CSRF-Token", "")
        if not sent:
            payload = request.get_json(silent=True) or {}
            sent = payload.get("csrf_token") or request.form.get("csrf_token") or ""
        if sent != session.get("csrf"):
            message = "Invalid or missing security token. Refresh the page and try again."
            if request.path.startswith("/api/") or request.is_json or request.headers.get("X-Requested-With") == "fetch":
                return jsonify({"error": message}), 400
            return render_template("error.html", message=message), 400
        return None

    @app.before_request
    def require_login():
        path = request.path
        if path.startswith("/static"):
            return None
        open_paths = {"/admin/login", "/api/auth/login", "/api/public/enquiries", "/api/public/contact", "/health"}
        if path in open_paths or not (path.startswith("/admin") or path.startswith("/api")):
            return None
        if "user_id" not in session:
            if path.startswith("/api"):
                return jsonify({"error": "Authentication required."}), 401
            return redirect(url_for("auth.login", next=path if path.startswith("/admin") else "/admin/"))
        return None

    @app.context_processor
    def inject_globals():
        from app.authz import current_user
        from app.constants import (
            BOOKING_STATUSES,
            CONVERSION_DEFINITION,
            ENQUIRY_STATUSES,
            PAYMENT_METHODS,
            PAYMENT_STATUSES,
            PROJECT_STATUSES,
            REVENUE_DEFINITION,
            STATUS_LABELS,
            TEAM_ROLES,
        )
        from app.models.settings import get as get_settings
        from app.utils import format_inr, label

        try:
            business = get_settings()
        except Exception:
            business = {"business_name": "FotoInsight Studio", "tagline": "", "email": "", "phone": "", "address": "", "city": "", "map_lat": 26.91, "map_lng": 75.78}
        user = current_user()
        notifications = []
        notification_count = 0
        show_demo = False
        if user and request.path.startswith("/admin"):
            try:
                from app.models.enquiry import open_count, recent_open
                scope = user["employee_id"] if user["role"] == "employee" else None
                notifications = recent_open(scope)
                notification_count = open_count(scope)
                show_demo = _has_demo_rows()
            except Exception:
                app.logger.exception("Could not load admin shell data")
        return {
            "csrf_token": session.get("csrf", ""),
            "current_user": user,
            "business": business,
            "status_labels": STATUS_LABELS,
            "label_for": label,
            "format_inr": format_inr,
            "enquiry_statuses": ENQUIRY_STATUSES,
            "booking_statuses": BOOKING_STATUSES,
            "project_statuses": PROJECT_STATUSES,
            "payment_methods": PAYMENT_METHODS,
            "payment_statuses": PAYMENT_STATUSES,
            "team_roles": TEAM_ROLES,
            "conversion_definition": CONVERSION_DEFINITION,
            "revenue_definition": REVENUE_DEFINITION,
            "notifications": notifications,
            "notification_count": notification_count,
            "show_demo_banner": show_demo,
        }

    @app.template_filter("inr")
    def inr_filter(value):
        from app.utils import format_inr
        return format_inr(value)

    @app.template_filter("status_label")
    def status_filter(value):
        from app.utils import label
        return label(value)

    from app.routes.analytics import bp as analytics_bp
    from app.routes.auth import bp as auth_bp
    from app.routes.bookings import bp as bookings_bp
    from app.routes.customers import bp as customers_bp
    from app.routes.dashboard import bp as dashboard_bp
    from app.routes.enquiries import bp as enquiries_bp
    from app.routes.payments import bp as payments_bp
    from app.routes.projects import bp as projects_bp
    from app.routes.public import bp as public_bp
    from app.routes.reports import bp as reports_bp
    from app.routes.services import bp as services_bp
    from app.routes.settings import bp as settings_bp

    for blueprint in (
        public_bp, auth_bp, dashboard_bp, customers_bp, enquiries_bp, bookings_bp,
        services_bp, payments_bp, projects_bp, analytics_bp, reports_bp, settings_bp,
    ):
        app.register_blueprint(blueprint)

    @app.errorhandler(AppError)
    def handle_app_error(err):
        if _json_error():
            return jsonify({"error": err.message}), err.status
        if err.status == 403 and session.get("user_id"):
            return render_template("admin/forbidden.html", message=err.message), 403
        return render_template("error.html", message=err.message), err.status

    @app.errorhandler(IntegrityError)
    def handle_integrity(err):
        app.logger.exception("Integrity error")
        message = "That record conflicts with existing data. It may be a duplicate or still linked to another record."
        if _json_error():
            return jsonify({"error": message}), 409
        return render_template("error.html", message=message), 409

    @app.errorhandler(OperationalError)
    def handle_database(err):
        app.logger.exception("Database error")
        message = "The database could not be reached. Check that MySQL is running and the .env settings are correct."
        if _json_error():
            return jsonify({"error": message}), 500
        return render_template("error.html", message=message), 500

    @app.errorhandler(RequestEntityTooLarge)
    def handle_large(_err):
        return jsonify({"error": "That file is larger than 2 MB."}), 413

    @app.errorhandler(404)
    def handle_404(_err):
        if _json_error():
            return jsonify({"error": "That record or page was not found."}), 404
        return render_template("error.html", message="That page was not found."), 404

    @app.errorhandler(500)
    def handle_500(_err):
        message = "Something went wrong while handling that request."
        if _json_error():
            return jsonify({"error": message}), 500
        return render_template("error.html", message=message), 500

    return app


def _json_error():
    return request.path.startswith("/api/") or request.is_json or request.headers.get("X-Requested-With") == "fetch"


def _has_demo_rows():
    row = query_one(
        """
        SELECT
            (SELECT COUNT(*) FROM customers WHERE is_demo = 1) +
            (SELECT COUNT(*) FROM bookings WHERE is_demo = 1) AS n
        """
    )
    return bool(row and row["n"])
