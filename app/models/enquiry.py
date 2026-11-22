"""Enquiries from the public site and from the admin desk."""

from app.db import IntegrityError, execute, query_all, query_one, transaction, tx_execute, tx_query_one
from app.errors import AppError
from app.utils import clean_row, clean_rows, code_for, like, pagination


def list_enquiries(q="", event_type="", status="", date_from=None, date_to=None, page=1, per_page=10, employee_id=None):
    where = ["1=1"]
    params = []
    if employee_id:
        where.append("e.assigned_employee_id = %s")
        params.append(employee_id)
    if q:
        pattern = like(q)
        where.append(
            "(e.full_name LIKE %s ESCAPE '\\\\' OR e.email LIKE %s ESCAPE '\\\\' OR e.phone LIKE %s ESCAPE '\\\\' OR e.enquiry_code LIKE %s ESCAPE '\\\\' OR e.city LIKE %s ESCAPE '\\\\')"
        )
        params.extend([pattern, pattern, pattern, pattern, pattern])
    if event_type:
        where.append("e.event_type = %s")
        params.append(event_type)
    if status:
        where.append("e.status = %s")
        params.append(status)
    if date_from:
        where.append("e.event_date >= %s")
        params.append(date_from)
    if date_to:
        where.append("e.event_date <= %s")
        params.append(date_to)
    base = f"""
        FROM enquiries e
        LEFT JOIN employees emp ON emp.id = e.assigned_employee_id
        LEFT JOIN packages pkg ON pkg.id = e.package_id
        WHERE {' AND '.join(where)}
    """
    total = query_one(f"SELECT COUNT(*) AS n {base}", params)["n"]
    page_info = pagination(total, page, per_page)
    rows = query_all(
        f"""
        SELECT e.*, emp.full_name AS assigned_name, pkg.name AS package_name
        {base}
        ORDER BY e.created_at DESC, e.id DESC
        LIMIT %s OFFSET %s
        """,
        params + [page_info["per_page"], page_info["offset"]],
    )
    return clean_rows(rows), page_info


def get(enquiry_id, employee_id=None):
    params = [enquiry_id]
    extra = ""
    if employee_id:
        extra = " AND e.assigned_employee_id = %s"
        params.append(employee_id)
    row = clean_row(
        query_one(
            f"""
            SELECT e.*, emp.full_name AS assigned_name, pkg.name AS package_name, b.booking_code, b.id AS booking_id
            FROM enquiries e
            LEFT JOIN employees emp ON emp.id = e.assigned_employee_id
            LEFT JOIN packages pkg ON pkg.id = e.package_id
            LEFT JOIN bookings b ON b.enquiry_id = e.id
            WHERE e.id = %s {extra}
            """,
            params,
        )
    )
    return row


def notes(enquiry_id):
    return clean_rows(
        query_all(
            """
            SELECT n.id, n.note, n.created_at, u.display_name
            FROM enquiry_notes n
            JOIN users u ON u.id = n.user_id
            WHERE n.enquiry_id = %s
            ORDER BY n.created_at DESC
            """,
            (enquiry_id,),
        )
    )


def _insert(db, data, is_demo=0):
    token = data.get("submission_token")
    if token:
        existing = tx_query_one(db, "SELECT id, enquiry_code FROM enquiries WHERE submission_token=%s", (token,))
        if existing:
            return {"id": existing["id"], "enquiry_code": existing["enquiry_code"], "duplicate": True}
    new_id = tx_execute(
        db,
        """
        INSERT INTO enquiries (
            enquiry_code, customer_id, full_name, email, phone, event_type, event_date,
            event_location, city, guest_count, package_id, estimated_budget, requirements,
            status, assigned_employee_id, submission_token, source, is_demo
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            f"TMP-{new_temp_code()}",
            data.get("customer_id"),
            data["full_name"],
            data["email"],
            data["phone"],
            data["event_type"],
            data.get("event_date"),
            data.get("event_location"),
            data.get("city"),
            data.get("guest_count"),
            data.get("package_id"),
            data.get("estimated_budget"),
            data.get("requirements"),
            data.get("status") or "new",
            data.get("assigned_employee_id"),
            token,
            data.get("source") or "website",
            is_demo,
        ),
    )
    code = code_for("ENQ", new_id)
    tx_execute(db, "UPDATE enquiries SET enquiry_code=%s WHERE id=%s", (code, new_id))
    return {"id": new_id, "enquiry_code": code, "duplicate": False}


def new_temp_code():
    import uuid
    return uuid.uuid4().hex[:12]


def create(data, is_demo=0):
    if data.get("package_id"):
        package = query_one("SELECT id, service_id FROM packages WHERE id=%s", (data["package_id"],))
        if not package:
            raise AppError("Choose a valid package.")
        service = query_one("SELECT name FROM services WHERE id=%s", (package["service_id"],))
        if service and data["event_type"] not in (service["name"], "General Contact") and data["event_type"] != service["name"]:
            if data["event_type"] != service["name"]:
                raise AppError("That package does not belong to the selected event type.")
    try:
        with transaction() as db:
            return _insert(db, data, is_demo=is_demo)
    except IntegrityError as exc:
        if data.get("submission_token"):
            existing = query_one(
                "SELECT id, enquiry_code FROM enquiries WHERE submission_token=%s",
                (data["submission_token"],),
            )
            if existing:
                return {"id": existing["id"], "enquiry_code": existing["enquiry_code"], "duplicate": True}
        raise AppError("The enquiry could not be saved because it conflicts with an existing record.", 409) from exc


def update(enquiry_id, data, employee_id=None):
    current = get(enquiry_id, employee_id=employee_id)
    if not current:
        raise AppError("Enquiry not found.", 404)
    if current["status"] == "converted" and data.get("status") not in (None, "converted"):
        linked = query_one("SELECT booking_code FROM bookings WHERE enquiry_id=%s", (enquiry_id,))
        if linked and data.get("status") != "converted":
            raise AppError(
                f"This enquiry is already booking {linked['booking_code']}. Change the booking instead of reopening the enquiry.",
                409,
            )
    execute(
        """
        UPDATE enquiries SET
            full_name=%s, email=%s, phone=%s, event_type=%s, event_date=%s, event_location=%s,
            city=%s, guest_count=%s, package_id=%s, estimated_budget=%s, requirements=%s, status=%s,
            assigned_employee_id=%s
        WHERE id=%s
        """,
        (
            data["full_name"], data["email"], data["phone"], data["event_type"], data.get("event_date"),
            data.get("event_location"), data.get("city"), data.get("guest_count"), data.get("package_id"),
            data.get("estimated_budget"), data.get("requirements"), data.get("status") or current["status"],
            data.get("assigned_employee_id") if "assigned_employee_id" in data else current["assigned_employee_id"],
            enquiry_id,
        ),
    )


def delete(enquiry_id):
    current = get(enquiry_id)
    if not current:
        raise AppError("Enquiry not found.", 404)
    linked = query_one("SELECT booking_code FROM bookings WHERE enquiry_id=%s", (enquiry_id,))
    if linked:
        raise AppError(f"This enquiry was converted to {linked['booking_code']}. Delete that booking first.", 409)
    execute("DELETE FROM enquiries WHERE id=%s", (enquiry_id,))


def assign(enquiry_id, employee_id):
    if not get(enquiry_id):
        raise AppError("Enquiry not found.", 404)
    if employee_id is not None and not query_one("SELECT id FROM employees WHERE id=%s AND status='active'", (employee_id,)):
        raise AppError("Choose an active employee.", 404)
    execute("UPDATE enquiries SET assigned_employee_id=%s WHERE id=%s", (employee_id, enquiry_id))


def add_note(enquiry_id, user_id, note, employee_id=None):
    if not get(enquiry_id, employee_id=employee_id):
        raise AppError("Enquiry not found.", 404)
    text = (note or "").strip()
    if not text:
        raise AppError("Write a note before saving.")
    if len(text) > 2000:
        raise AppError("Note must be 2000 characters or fewer.")
    return execute(
        "INSERT INTO enquiry_notes (enquiry_id, user_id, note) VALUES (%s, %s, %s)",
        (enquiry_id, user_id, text),
    )


def event_types():
    rows = query_all("SELECT DISTINCT event_type FROM enquiries ORDER BY event_type")
    return [row["event_type"] for row in rows]


def recent_open(employee_id=None, limit=6):
    params = []
    extra = ""
    if employee_id:
        extra = " AND e.assigned_employee_id = %s"
        params.append(employee_id)
    else:
        extra = " AND e.status = 'new'"
    params.append(limit)
    rows = query_all(
        f"""
        SELECT e.id, e.enquiry_code, e.full_name, e.event_type, e.status, e.created_at
        FROM enquiries e
        WHERE e.status IN ('new', 'follow_up', 'negotiation') {extra}
        ORDER BY e.created_at DESC
        LIMIT %s
        """,
        params,
    )
    return clean_rows(rows)


def open_count(employee_id=None):
    if employee_id:
        row = query_one(
            """
            SELECT COUNT(*) AS n FROM enquiries
            WHERE assigned_employee_id=%s AND status IN ('new','contacted','follow_up','negotiation')
            """,
            (employee_id,),
        )
    else:
        row = query_one("SELECT COUNT(*) AS n FROM enquiries WHERE status='new'")
    return row["n"]
