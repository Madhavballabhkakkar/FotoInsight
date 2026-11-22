"""Check form input on the server. The browser checks too, but the server decides."""

import re
from decimal import Decimal, InvalidOperation

from app.constants import (
    BOOKING_STATUSES,
    ENQUIRY_STATUSES,
    PAYMENT_METHODS,
    PAYMENT_STATUSES,
    PROJECT_STATUSES,
)
from app.errors import AppError

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def _text(data, key):
    value = data.get(key, "")
    if value is None:
        return ""
    return str(value).strip()


def require_text(data, key, label, max_len=150):
    value = _text(data, key)
    if not value:
        raise AppError(f"{label} is required.")
    if len(value) > max_len:
        raise AppError(f"{label} must be {max_len} characters or fewer.")
    return value


def optional_text(data, key, label, max_len=255):
    value = _text(data, key)
    if not value:
        return None
    if len(value) > max_len:
        raise AppError(f"{label} must be {max_len} characters or fewer.")
    return value


def require_email(data, key="email"):
    value = require_text(data, key, "Email address", 150).lower()
    if not EMAIL_RE.match(value):
        raise AppError("Enter a valid email address.")
    return value


def require_phone(data, key="phone"):
    raw = require_text(data, key, "Phone number", 20)
    digits = re.sub(r"\D", "", raw)
    if len(digits) < 10 or len(digits) > 15:
        raise AppError("Phone number should contain 10 to 15 digits.")
    return raw


def optional_date(data, key, label):
    value = _text(data, key)
    if not value:
        return None
    from app.utils import as_date

    try:
        return as_date(value)
    except AppError as exc:
        raise AppError(f"{label} must be a valid date.") from exc


def require_date(data, key, label):
    parsed = optional_date(data, key, label)
    if parsed is None:
        raise AppError(f"{label} is required.")
    return parsed


def optional_int(data, key, label, minimum=0, maximum=100000):
    value = _text(data, key)
    if not value:
        return None
    if not re.fullmatch(r"-?\d+", value):
        raise AppError(f"{label} must be a whole number.")
    number = int(value)
    if number < minimum or number > maximum:
        raise AppError(f"{label} must be between {minimum} and {maximum}.")
    return number


def require_money(data, key, label, minimum=Decimal("0.01")):
    value = _text(data, key)
    if not value:
        raise AppError(f"{label} is required.")
    try:
        amount = Decimal(value)
    except InvalidOperation as exc:
        raise AppError(f"{label} must be a number.") from exc
    if amount < minimum:
        raise AppError(f"{label} must be at least {minimum}.")
    if amount > Decimal("100000000"):
        raise AppError(f"{label} is too large.")
    return amount.quantize(Decimal("0.01"))


def optional_money(data, key, label):
    value = _text(data, key)
    if not value:
        return None
    return require_money(data, key, label, minimum=Decimal("0"))


def choice(data, key, label, options, required=True):
    value = _text(data, key)
    allowed = {item[0] if isinstance(item, tuple) else item for item in options}
    if not value:
        if required:
            raise AppError(f"{label} is required.")
        return None
    if value not in allowed:
        raise AppError(f"Choose a valid {label.lower()}.")
    return value


def password_pair(new_password):
    password = new_password or ""
    if len(password) < 8:
        raise AppError("Password must be at least 8 characters.")
    if not re.search(r"[A-Za-z]", password) or not re.search(r"\d", password):
        raise AppError("Password must include a letter and a number.")
    return password


def customer_payload(data, partial=False):
    payload = {
        "full_name": require_text(data, "full_name", "Full name"),
        "email": require_email(data),
        "phone": require_phone(data),
        "city": require_text(data, "city", "City", 80),
        "address": optional_text(data, "address", "Address"),
    }
    if not partial or _text(data, "registration_date"):
        payload["registration_date"] = require_date(data, "registration_date", "Registration date") if not partial else (
            optional_date(data, "registration_date", "Registration date") or require_date(data, "registration_date", "Registration date")
        )
    else:
        payload["registration_date"] = require_date(data, "registration_date", "Registration date")
    return payload


def enquiry_payload(data, source="website"):
    token = _text(data, "submission_token")
    if source == "website" or token:
        if not TOKEN_RE.match(token):
            raise AppError("The form token was missing. Refresh the page and submit again.")
    event_date = require_date(data, "event_date", "Event date") if source == "website" else optional_date(data, "event_date", "Event date")
    package_raw = _text(data, "package_id")
    package_id = int(package_raw) if package_raw.isdigit() else None
    if package_raw and package_id is None:
        raise AppError("Choose a valid package.")
    return {
        "full_name": require_text(data, "full_name", "Full name"),
        "email": require_email(data),
        "phone": require_phone(data),
        "event_type": require_text(data, "event_type", "Event type", 80),
        "event_date": event_date,
        "event_location": require_text(data, "event_location", "Event location", 180) if source == "website" else optional_text(data, "event_location", "Event location", 180),
        "city": optional_text(data, "city", "City", 80),
        "guest_count": optional_int(data, "guest_count", "Number of guests", 0, 50000),
        "package_id": package_id,
        "estimated_budget": optional_money(data, "estimated_budget", "Estimated budget"),
        "requirements": optional_text(data, "requirements", "Additional requirements", 2000),
        "status": choice(data, "status", "Status", ENQUIRY_STATUSES, required=False) or "new",
        "assigned_employee_id": optional_int(data, "assigned_employee_id", "Employee", 1, 1000000),
        "submission_token": token or None,
        "source": source,
    }


def contact_payload(data):
    token = _text(data, "submission_token")
    if not TOKEN_RE.match(token):
        raise AppError("The form token was missing. Refresh the page and submit again.")
    return {
        "full_name": require_text(data, "full_name", "Full name"),
        "email": require_email(data),
        "phone": require_phone(data),
        "event_type": "General Contact",
        "event_date": None,
        "event_location": "Not specified",
        "city": None,
        "guest_count": None,
        "package_id": None,
        "estimated_budget": None,
        "requirements": require_text(data, "message", "Message", 2000),
        "status": "new",
        "assigned_employee_id": None,
        "submission_token": token,
        "source": "contact",
    }


def service_payload(data):
    return {
        "name": require_text(data, "name", "Service name", 120),
        "category": require_text(data, "category", "Category", 80),
        "description": require_text(data, "description", "Description", 2000),
        "base_price": require_money(data, "base_price", "Base price", minimum=Decimal("0")),
        "status": choice(data, "status", "Status", ["active", "inactive"]),
        "sort_order": optional_int(data, "sort_order", "Sort order", 0, 999) or 0,
    }


def package_payload(data):
    service_raw = _text(data, "service_id")
    if not service_raw.isdigit():
        raise AppError("Choose a service for this package.")
    return {
        "service_id": int(service_raw),
        "name": require_text(data, "name", "Package name", 150),
        "description": optional_text(data, "description", "Description", 2000),
        "price": require_money(data, "price", "Package price", minimum=Decimal("0")),
        "inclusions": optional_text(data, "inclusions", "Inclusions", 2000),
        "status": choice(data, "status", "Status", ["active", "inactive"]),
    }


def booking_payload(data):
    customer_raw = _text(data, "customer_id")
    service_raw = _text(data, "service_id")
    if not customer_raw.isdigit():
        raise AppError("Choose a customer.")
    if not service_raw.isdigit():
        raise AppError("Choose a service.")
    package_raw = _text(data, "package_id")
    enquiry_raw = _text(data, "enquiry_id")
    team = data.get("team") or []
    if not isinstance(team, list):
        raise AppError("The assigned team was not sent correctly.")
    return {
        "customer_id": int(customer_raw),
        "service_id": int(service_raw),
        "package_id": int(package_raw) if package_raw.isdigit() else None,
        "enquiry_id": int(enquiry_raw) if enquiry_raw.isdigit() else None,
        "event_name": require_text(data, "event_name", "Event name", 180),
        "event_date": require_date(data, "event_date", "Event date"),
        "event_location": require_text(data, "event_location", "Event location", 180),
        "city": require_text(data, "city", "City", 80),
        "total_amount": require_money(data, "total_amount", "Total amount"),
        "status": choice(data, "status", "Booking status", BOOKING_STATUSES),
        "notes": optional_text(data, "notes", "Notes", 2000),
        "team": team,
    }


def payment_payload(data):
    booking_raw = _text(data, "booking_id")
    if not booking_raw.isdigit():
        raise AppError("Choose a booking.")
    return {
        "booking_id": int(booking_raw),
        "amount": require_money(data, "amount", "Amount"),
        "payment_date": require_date(data, "payment_date", "Payment date"),
        "method": choice(data, "method", "Payment method", PAYMENT_METHODS),
        "transaction_ref": optional_text(data, "transaction_ref", "Transaction reference", 80),
        "status": choice(data, "status", "Payment status", PAYMENT_STATUSES),
        "notes": optional_text(data, "notes", "Notes", 255),
    }


def project_payload(data):
    booking_raw = _text(data, "booking_id")
    if not booking_raw.isdigit():
        raise AppError("Choose a booking.")
    photographer = _text(data, "photographer_id")
    editor = _text(data, "editor_id")
    return {
        "booking_id": int(booking_raw),
        "photographer_id": int(photographer) if photographer.isdigit() else None,
        "editor_id": int(editor) if editor.isdigit() else None,
        "start_date": optional_date(data, "start_date", "Start date"),
        "delivery_date": optional_date(data, "delivery_date", "Delivery date"),
        "status": choice(data, "status", "Project status", PROJECT_STATUSES),
        "notes": optional_text(data, "notes", "Notes", 2000),
    }


def employee_payload(data):
    return {
        "full_name": require_text(data, "full_name", "Full name", 120),
        "email": require_email(data),
        "phone": require_phone(data),
        "job_title": require_text(data, "job_title", "Job title", 80),
        "city": require_text(data, "city", "City", 80),
        "status": choice(data, "status", "Status", ["active", "inactive"]),
    }


def settings_payload(data):
    from decimal import Decimal as D

    lat = _text(data, "map_lat")
    lng = _text(data, "map_lng")
    try:
        lat_n = D(lat)
        lng_n = D(lng)
    except InvalidOperation as exc:
        raise AppError("Map latitude and longitude must be numbers.") from exc
    if not (D("-90") <= lat_n <= D("90") and D("-180") <= lng_n <= D("180")):
        raise AppError("Map coordinates are out of range.")
    return {
        "business_name": require_text(data, "business_name", "Business name", 150),
        "tagline": require_text(data, "tagline", "Tagline", 255),
        "email": require_email(data),
        "phone": require_text(data, "phone", "Phone", 30),
        "address": require_text(data, "address", "Address"),
        "city": require_text(data, "city", "City", 80),
        "map_lat": lat_n.quantize(D("0.000001")),
        "map_lng": lng_n.quantize(D("0.000001")),
        "instagram_url": optional_text(data, "instagram_url", "Instagram URL"),
        "facebook_url": optional_text(data, "facebook_url", "Facebook URL"),
        "youtube_url": optional_text(data, "youtube_url", "YouTube URL"),
        "about_intro": optional_text(data, "about_intro", "About introduction", 2000),
        "mission": optional_text(data, "mission", "Mission", 2000),
        "vision": optional_text(data, "vision", "Vision", 2000),
    }
