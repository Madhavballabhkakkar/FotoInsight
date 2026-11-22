"""Photography projects created from bookings. One project per booking."""

import uuid
from datetime import date, timedelta

from app.db import execute, query_all, query_one
from app.errors import AppError
from app.utils import clean_row, clean_rows, code_for, like, pagination


def _scope(employee_id, params):
    if not employee_id:
        return ""
    params.extend([employee_id, employee_id])
    return " AND (pr.photographer_id = %s OR pr.editor_id = %s)"


def list_projects(q="", status="", delayed=False, page=1, per_page=10, employee_id=None):
    where = ["1=1"]
    params = []
    scope = _scope(employee_id, params)
    if q:
        pattern = like(q)
        where.append("(pr.project_code LIKE %s ESCAPE '\\\\' OR b.event_name LIKE %s ESCAPE '\\\\' OR c.full_name LIKE %s ESCAPE '\\\\')")
        params.extend([pattern, pattern, pattern])
    if status:
        where.append("pr.status = %s")
        params.append(status)
    if delayed:
        where.append("pr.delivery_date < CURDATE() AND pr.status NOT IN ('completed','delivered')")
    base = f"""
        FROM projects pr
        JOIN bookings b ON b.id = pr.booking_id
        JOIN customers c ON c.id = b.customer_id
        LEFT JOIN employees ph ON ph.id = pr.photographer_id
        LEFT JOIN employees ed ON ed.id = pr.editor_id
        WHERE {' AND '.join(where)} {scope}
    """
    total = query_one(f"SELECT COUNT(*) AS n {base}", params)["n"]
    page_info = pagination(total, page, per_page)
    rows = query_all(
        f"""
        SELECT pr.*, b.booking_code, b.event_name, b.event_date, c.full_name AS customer_name,
               ph.full_name AS photographer_name, ed.full_name AS editor_name,
               CASE WHEN pr.delivery_date < CURDATE() AND pr.status NOT IN ('completed','delivered') THEN 1 ELSE 0 END AS is_delayed
        {base}
        ORDER BY pr.delivery_date IS NULL, pr.delivery_date, pr.id DESC
        LIMIT %s OFFSET %s
        """,
        params + [page_info["per_page"], page_info["offset"]],
    )
    return clean_rows(rows), page_info


def get(project_id, employee_id=None):
    params = [project_id]
    scope = _scope(employee_id, params)
    row = query_one(
        f"""
        SELECT pr.*, b.booking_code, b.event_name, b.event_date, b.event_location, b.city,
               c.full_name AS customer_name, c.id AS customer_id,
               ph.full_name AS photographer_name, ed.full_name AS editor_name,
               CASE WHEN pr.delivery_date < CURDATE() AND pr.status NOT IN ('completed','delivered') THEN 1 ELSE 0 END AS is_delayed
        FROM projects pr
        JOIN bookings b ON b.id = pr.booking_id
        JOIN customers c ON c.id = b.customer_id
        LEFT JOIN employees ph ON ph.id = pr.photographer_id
        LEFT JOIN employees ed ON ed.id = pr.editor_id
        WHERE pr.id=%s {scope}
        """,
        params,
    )
    return clean_row(row)


def create(data, is_demo=0):
    booking = query_one("SELECT id, event_date, is_demo FROM bookings WHERE id=%s", (data["booking_id"],))
    if not booking:
        raise AppError("Booking not found.", 404)
    if query_one("SELECT id FROM projects WHERE booking_id=%s", (data["booking_id"],)):
        raise AppError("This booking already has a project.", 409)
    start = data.get("start_date") or booking["event_date"]
    delivery = data.get("delivery_date") or (booking["event_date"] + timedelta(days=21) if booking["event_date"] else None)
    if start and delivery and delivery < start:
        raise AppError("Delivery date cannot be before the project start date.")
    project_id = execute(
        """
        INSERT INTO projects (
            project_code, booking_id, photographer_id, editor_id, start_date, delivery_date, status, notes, is_demo
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (f"TMP-{uuid.uuid4().hex[:12]}", data["booking_id"], data.get("photographer_id"), data.get("editor_id"), start, delivery, data["status"], data.get("notes"), is_demo or booking["is_demo"]),
    )
    code = code_for("PRJ", project_id)
    execute("UPDATE projects SET project_code=%s WHERE id=%s", (code, project_id))
    return {"id": project_id, "project_code": code}


def update(project_id, data, fields=None):
    current = get(project_id)
    if not current:
        raise AppError("Project not found.", 404)
    payload = {
        "photographer_id": data.get("photographer_id", current["photographer_id"]),
        "editor_id": data.get("editor_id", current["editor_id"]),
        "start_date": data.get("start_date", current["start_date"]),
        "delivery_date": data.get("delivery_date", current["delivery_date"]),
        "status": data.get("status", current["status"]),
        "notes": data.get("notes", current["notes"]),
    }
    if fields is not None:
        for key in list(payload):
            if key not in fields and key in current:
                payload[key] = current[key]
    if payload["start_date"] and payload["delivery_date"] and str(payload["delivery_date"]) < str(payload["start_date"]):
        raise AppError("Delivery date cannot be before the project start date.")
    execute(
        """
        UPDATE projects
        SET photographer_id=%s, editor_id=%s, start_date=%s, delivery_date=%s, status=%s, notes=%s
        WHERE id=%s
        """,
        (
            payload["photographer_id"], payload["editor_id"], payload["start_date"], payload["delivery_date"],
            payload["status"], payload["notes"], project_id,
        ),
    )


def delete(project_id):
    if not get(project_id):
        raise AppError("Project not found.", 404)
    execute("DELETE FROM projects WHERE id=%s", (project_id,))


def bookings_without_project():
    return clean_rows(
        query_all(
            """
            SELECT b.id, b.booking_code, b.event_name, b.event_date, c.full_name AS customer_name
            FROM bookings b
            JOIN customers c ON c.id = b.customer_id
            LEFT JOIN projects pr ON pr.booking_id = b.id
            WHERE pr.id IS NULL AND b.status <> 'cancelled'
            ORDER BY b.event_date
            """
        )
    )
