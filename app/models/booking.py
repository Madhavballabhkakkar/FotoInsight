"""Bookings. An enquiry can become a booking only once."""

import uuid
from decimal import Decimal

from app.db import execute, query_all, query_one, transaction, tx_execute, tx_query_one
from app.errors import AppError
from app.utils import clean_row, clean_rows, code_for, like, pagination

RECEIVED_SQL = """
COALESCE((
    SELECT SUM(CASE
        WHEN p.status IN ('paid', 'partially_paid') THEN p.amount
        WHEN p.status = 'refunded' THEN -p.amount
        ELSE 0 END)
    FROM payments p WHERE p.booking_id = b.id
), 0)
"""


def _scope(employee_id, params, alias="b"):
    if not employee_id:
        return ""
    params.append(employee_id)
    return f"""
        AND EXISTS (
            SELECT 1 FROM booking_team bt
            WHERE bt.booking_id = {alias}.id AND bt.employee_id = %s
        )
    """


def list_bookings(q="", status="", event_type="", date_from=None, date_to=None, page=1, per_page=10, employee_id=None):
    where = ["1=1"]
    params = []
    scope = _scope(employee_id, params)
    if q:
        pattern = like(q)
        where.append("(b.booking_code LIKE %s ESCAPE '\\\\' OR b.event_name LIKE %s ESCAPE '\\\\' OR c.full_name LIKE %s ESCAPE '\\\\' OR b.city LIKE %s ESCAPE '\\\\')")
        params.extend([pattern, pattern, pattern, pattern])
    if status:
        where.append("b.status = %s")
        params.append(status)
    if event_type:
        where.append("b.event_type = %s")
        params.append(event_type)
    if date_from:
        where.append("b.event_date >= %s")
        params.append(date_from)
    if date_to:
        where.append("b.event_date <= %s")
        params.append(date_to)
    base = f"""
        FROM bookings b
        JOIN customers c ON c.id = b.customer_id
        JOIN services s ON s.id = b.service_id
        WHERE {' AND '.join(where)} {scope}
    """
    total = query_one(f"SELECT COUNT(*) AS n {base}", params)["n"]
    page_info = pagination(total, page, per_page)
    rows = query_all(
        f"""
        SELECT b.*, c.full_name AS customer_name, s.name AS service_name, {RECEIVED_SQL} AS received
        {base}
        ORDER BY b.event_date ASC, b.id DESC
        LIMIT %s OFFSET %s
        """,
        params + [page_info["per_page"], page_info["offset"]],
    )
    return [_with_balance(row) for row in clean_rows(rows)], page_info


def month_events(year, month, employee_id=None):
    params = [year, month]
    scope = _scope(employee_id, params)
    rows = query_all(
        f"""
        SELECT b.id, b.booking_code, b.event_name, b.event_date, b.city, b.status, c.full_name AS customer_name
        FROM bookings b
        JOIN customers c ON c.id = b.customer_id
        WHERE YEAR(b.event_date)=%s AND MONTH(b.event_date)=%s {scope}
        ORDER BY b.event_date, b.event_name
        """,
        params,
    )
    return clean_rows(rows)


def get(booking_id, employee_id=None):
    params = [booking_id]
    scope = _scope(employee_id, params)
    row = query_one(
        f"""
        SELECT b.*, c.full_name AS customer_name, c.email AS customer_email, c.phone AS customer_phone,
               s.name AS service_name, pkg.name AS package_name, e.enquiry_code,
               {RECEIVED_SQL} AS received
        FROM bookings b
        JOIN customers c ON c.id = b.customer_id
        JOIN services s ON s.id = b.service_id
        LEFT JOIN packages pkg ON pkg.id = b.package_id
        LEFT JOIN enquiries e ON e.id = b.enquiry_id
        WHERE b.id=%s {scope}
        """,
        params,
    )
    if not row:
        return None
    booking = _with_balance(clean_row(row))
    booking["team"] = team(booking_id)
    booking["payments"] = clean_rows(
        query_all(
            "SELECT * FROM payments WHERE booking_id=%s ORDER BY payment_date, id",
            (booking_id,),
        )
    )
    return booking


def team(booking_id):
    return clean_rows(
        query_all(
            """
            SELECT bt.id, bt.employee_id, bt.team_role, bt.is_lead, emp.full_name, emp.job_title
            FROM booking_team bt
            JOIN employees emp ON emp.id = bt.employee_id
            WHERE bt.booking_id=%s
            ORDER BY bt.is_lead DESC, emp.full_name
            """,
            (booking_id,),
        )
    )


def _with_balance(row):
    received = round(float(row.get("received") or 0), 2)
    total = round(float(row["total_amount"]), 2)
    row["received"] = received
    row["outstanding"] = round(total - received, 2)
    row["advance_payment"] = received
    row["remaining_amount"] = row["outstanding"]
    if received <= 0:
        row["collection_status"] = "pending"
    elif received + 0.009 < total:
        row["collection_status"] = "partially_paid"
    else:
        row["collection_status"] = "paid"
    return row


def _validate_links(db, data):
    customer = tx_query_one(db, "SELECT id FROM customers WHERE id=%s", (data["customer_id"],))
    if not customer:
        raise AppError("Choose a valid customer.", 404)
    service = tx_query_one(db, "SELECT id, name, base_price FROM services WHERE id=%s", (data["service_id"],))
    if not service:
        raise AppError("Choose a valid service.", 404)
    package_id = data.get("package_id")
    if package_id:
        package = tx_query_one(db, "SELECT id, service_id FROM packages WHERE id=%s", (package_id,))
        if not package or package["service_id"] != data["service_id"]:
            raise AppError("That package does not belong to the selected service.")
    return service


def _replace_team(db, booking_id, team_rows):
    tx_execute(db, "DELETE FROM booking_team WHERE booking_id=%s", (booking_id,))
    seen = set()
    lead_set = False
    for item in team_rows:
        if not isinstance(item, dict):
            raise AppError("Each team member needs an employee and a role.")
        employee_raw = str(item.get("employee_id") or "")
        role = str(item.get("team_role") or "").strip()
        if not employee_raw.isdigit() or not role:
            continue
        employee_id = int(employee_raw)
        key = (employee_id, role)
        if key in seen:
            continue
        seen.add(key)
        employee = tx_query_one(db, "SELECT id FROM employees WHERE id=%s", (employee_id,))
        if not employee:
            raise AppError("One of the assigned employees does not exist.", 404)
        is_lead = 1 if item.get("is_lead") in (True, 1, "1", "true", "on") else 0
        if is_lead and lead_set:
            is_lead = 0
        if is_lead:
            lead_set = True
        tx_execute(
            db,
            "INSERT INTO booking_team (booking_id, employee_id, team_role, is_lead) VALUES (%s, %s, %s, %s)",
            (booking_id, employee_id, role[:60], is_lead),
        )


def create(data, is_demo=0):
    with transaction() as db:
        return _create(db, data, is_demo=is_demo)


def _create(db, data, is_demo=0):
    service = _validate_links(db, data)
    enquiry_id = data.get("enquiry_id")
    if enquiry_id:
        enquiry = tx_query_one(db, "SELECT * FROM enquiries WHERE id=%s FOR UPDATE", (enquiry_id,))
        if not enquiry:
            raise AppError("Enquiry not found.", 404)
        if enquiry["status"] == "converted":
            raise AppError("This enquiry was already converted. A second booking was not created.", 409)
        existing = tx_query_one(db, "SELECT id, booking_code FROM bookings WHERE enquiry_id=%s", (enquiry_id,))
        if existing:
            raise AppError(f"This enquiry is already linked to {existing['booking_code']}.", 409)
    total = Decimal(str(data["total_amount"])).quantize(Decimal("0.01"))
    if total <= 0:
        raise AppError("Total amount must be greater than zero.")
    temp = f"TMP-{uuid.uuid4().hex[:12]}"
    booking_id = tx_execute(
        db,
        """
        INSERT INTO bookings (
            booking_code, customer_id, enquiry_id, service_id, package_id, event_name, event_type,
            event_date, event_location, city, total_amount, status, notes, is_demo
        ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """,
        (
            temp[:30],
            data["customer_id"],
            enquiry_id,
            data["service_id"],
            data.get("package_id"),
            data["event_name"],
            service["name"],
            data["event_date"],
            data["event_location"],
            data["city"],
            total,
            data["status"],
            data.get("notes"),
            is_demo,
        ),
    )
    code = code_for("BKG", booking_id)
    tx_execute(db, "UPDATE bookings SET booking_code=%s WHERE id=%s", (code, booking_id))
    if enquiry_id:
        tx_execute(
            db,
            "UPDATE enquiries SET status='converted', customer_id=%s WHERE id=%s",
            (data["customer_id"], enquiry_id),
        )
    _replace_team(db, booking_id, data.get("team") or [])
    return {"id": booking_id, "booking_code": code}


def update(booking_id, data):
    with transaction() as db:
        current = tx_query_one(db, "SELECT * FROM bookings WHERE id=%s FOR UPDATE", (booking_id,))
        if not current:
            raise AppError("Booking not found.", 404)
        service = _validate_links(db, data)
        total = Decimal(str(data["total_amount"])).quantize(Decimal("0.01"))
        received_row = tx_query_one(
            db,
            """
            SELECT COALESCE(SUM(CASE
                WHEN status IN ('paid','partially_paid') THEN amount
                WHEN status='refunded' THEN -amount ELSE 0 END), 0) AS received
            FROM payments WHERE booking_id=%s
            """,
            (booking_id,),
        )
        received = Decimal(str(received_row["received"] or 0))
        if total < received:
            raise AppError(
                f"The booking total cannot be lower than the INR {received} already collected. Record a refund first.",
                409,
            )
        tx_execute(
            db,
            """
            UPDATE bookings SET
                customer_id=%s, service_id=%s, package_id=%s, event_name=%s, event_type=%s,
                event_date=%s, event_location=%s, city=%s, total_amount=%s, status=%s, notes=%s
            WHERE id=%s
            """,
            (
                data["customer_id"], data["service_id"], data.get("package_id"), data["event_name"], service["name"],
                data["event_date"], data["event_location"], data["city"], total, data["status"], data.get("notes"),
                booking_id,
            ),
        )
        if "team" in data:
            _replace_team(db, booking_id, data.get("team") or [])


def update_status(booking_id, status, employee_id=None):
    current = get(booking_id, employee_id=employee_id)
    if not current:
        raise AppError("Booking not found.", 404)
    execute("UPDATE bookings SET status=%s WHERE id=%s", (status, booking_id))


def delete(booking_id):
    with transaction() as db:
        current = tx_query_one(db, "SELECT * FROM bookings WHERE id=%s FOR UPDATE", (booking_id,))
        if not current:
            raise AppError("Booking not found.", 404)
        if current["enquiry_id"]:
            tx_execute(
                db,
                "UPDATE enquiries SET status='negotiation' WHERE id=%s AND status='converted'",
                (current["enquiry_id"],),
            )
            tx_execute(db, "UPDATE bookings SET enquiry_id=NULL WHERE id=%s", (booking_id,))
        tx_execute(db, "DELETE FROM bookings WHERE id=%s", (booking_id,))


def choices(employee_id=None):
    params = []
    scope = _scope(employee_id, params)
    return clean_rows(
        query_all(
            f"""
            SELECT b.id, b.booking_code, b.event_name, b.event_date, b.total_amount, c.full_name AS customer_name
            FROM bookings b
            JOIN customers c ON c.id = b.customer_id
            WHERE 1=1 {scope}
            ORDER BY b.event_date DESC
            """,
            params,
        )
    )


def unlinked_enquiries():
    return clean_rows(
        query_all(
            """
            SELECT e.id, e.enquiry_code, e.full_name, e.event_type, e.event_date, e.estimated_budget, e.customer_id
            FROM enquiries e
            LEFT JOIN bookings b ON b.enquiry_id = e.id
            WHERE b.id IS NULL AND e.status <> 'rejected'
            ORDER BY e.created_at DESC
            LIMIT 200
            """
        )
    )
