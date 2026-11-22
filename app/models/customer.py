"""Customers. Booking counts and spending are calculated, never typed in by hand."""

from datetime import date

from app.db import execute, query_all, query_one
from app.errors import AppError
from app.utils import clean_row, clean_rows, like, pagination

SPENDING_SQL = """
COALESCE((
    SELECT SUM(CASE
        WHEN p.status IN ('paid', 'partially_paid') THEN p.amount
        WHEN p.status = 'refunded' THEN -p.amount
        ELSE 0 END)
    FROM payments p
    JOIN bookings b ON b.id = p.booking_id
    WHERE b.customer_id = c.id
), 0)
"""

BOOKING_COUNT_SQL = "(SELECT COUNT(*) FROM bookings b WHERE b.customer_id = c.id)"


def _employee_filter(employee_id, params):
    if not employee_id:
        return ""
    params.extend([employee_id, employee_id])
    return """
        AND (
            c.id IN (SELECT e.customer_id FROM enquiries e WHERE e.assigned_employee_id = %s AND e.customer_id IS NOT NULL)
            OR c.id IN (
                SELECT b.customer_id FROM bookings b
                JOIN booking_team bt ON bt.booking_id = b.id
                WHERE bt.employee_id = %s
            )
        )
    """


def list_customers(q="", city="", sort="newest", page=1, per_page=10, employee_id=None):
    where = ["1=1"]
    params = []
    if q:
        pattern = like(q)
        where.append("(c.full_name LIKE %s ESCAPE '\\\\' OR c.email LIKE %s ESCAPE '\\\\' OR c.phone LIKE %s ESCAPE '\\\\' OR CAST(c.id AS CHAR) LIKE %s ESCAPE '\\\\')")
        params.extend([pattern, pattern, pattern, pattern])
    if city:
        where.append("c.city = %s")
        params.append(city)
    employee_sql = _employee_filter(employee_id, params)
    sorts = {
        "name": "c.full_name ASC",
        "newest": "c.registration_date DESC, c.id DESC",
        "spending": "total_spending DESC, c.full_name ASC",
        "bookings": "total_bookings DESC, c.full_name ASC",
    }
    order = sorts.get(sort, sorts["newest"])
    base = f"""
        FROM customers c
        WHERE {' AND '.join(where)} {employee_sql}
    """
    total = query_one(f"SELECT COUNT(*) AS n {base}", params)["n"]
    page_info = pagination(total, page, per_page)
    rows = query_all(
        f"""
        SELECT c.*, {BOOKING_COUNT_SQL} AS total_bookings, {SPENDING_SQL} AS total_spending
        {base}
        ORDER BY {order}
        LIMIT %s OFFSET %s
        """,
        params + [page_info["per_page"], page_info["offset"]],
    )
    return clean_rows(rows), page_info


def cities(employee_id=None):
    params = []
    extra = _employee_filter(employee_id, params)
    rows = query_all(f"SELECT DISTINCT c.city FROM customers c WHERE 1=1 {extra} ORDER BY c.city", params)
    return [row["city"] for row in rows]


def get(customer_id, employee_id=None):
    params = [customer_id]
    extra = _employee_filter(employee_id, params)
    row = query_one(
        f"""
        SELECT c.*, {BOOKING_COUNT_SQL} AS total_bookings, {SPENDING_SQL} AS total_spending
        FROM customers c
        WHERE c.id = %s {extra}
        """,
        params,
    )
    return clean_row(row)


def history(customer_id):
    rows = query_all(
        """
        SELECT b.id, b.booking_code, b.event_name, b.event_type, b.event_date, b.city,
               b.total_amount, b.status,
               COALESCE(SUM(CASE
                   WHEN p.status IN ('paid', 'partially_paid') THEN p.amount
                   WHEN p.status = 'refunded' THEN -p.amount
                   ELSE 0 END), 0) AS received
        FROM bookings b
        LEFT JOIN payments p ON p.booking_id = b.id
        WHERE b.customer_id = %s
        GROUP BY b.id
        ORDER BY b.event_date DESC
        """,
        (customer_id,),
    )
    cleaned = []
    for row in clean_rows(rows):
        row["outstanding"] = round(row["total_amount"] - row["received"], 2)
        cleaned.append(row)
    return cleaned


def create(data, is_demo=0):
    registration = data.get("registration_date") or date.today()
    return execute(
        """
        INSERT INTO customers (full_name, email, phone, city, address, registration_date, is_demo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (data["full_name"], data["email"], data["phone"], data["city"], data.get("address"), registration, is_demo),
    )


def update(customer_id, data, employee_id=None):
    if not get(customer_id, employee_id=employee_id):
        raise AppError("Customer not found.", 404)
    execute(
        """
        UPDATE customers
        SET full_name=%s, email=%s, phone=%s, city=%s, address=%s, registration_date=%s
        WHERE id=%s
        """,
        (
            data["full_name"], data["email"], data["phone"], data["city"], data.get("address"),
            data["registration_date"], customer_id,
        ),
    )


def delete(customer_id):
    if not get(customer_id):
        raise AppError("Customer not found.", 404)
    bookings = query_one("SELECT COUNT(*) AS n FROM bookings WHERE customer_id=%s", (customer_id,))["n"]
    if bookings:
        raise AppError("This customer has bookings and cannot be deleted. Remove those bookings first.", 409)
    enquiries = query_one("SELECT COUNT(*) AS n FROM enquiries WHERE customer_id=%s", (customer_id,))["n"]
    if enquiries:
        raise AppError("This customer is linked to enquiries and cannot be deleted.", 409)
    execute("DELETE FROM customer_feedback WHERE customer_id=%s", (customer_id,))
    execute("DELETE FROM customers WHERE id=%s", (customer_id,))


def choices(employee_id=None):
    params = []
    extra = _employee_filter(employee_id, params)
    return clean_rows(
        query_all(
            f"SELECT c.id, c.full_name, c.city, c.email FROM customers c WHERE 1=1 {extra} ORDER BY c.full_name",
            params,
        )
    )


def public_feedback(limit=6):
    return clean_rows(
        query_all(
            """
            SELECT f.comment, f.rating, c.full_name, c.city
            FROM customer_feedback f
            JOIN customers c ON c.id = f.customer_id
            WHERE f.is_public = 1
            ORDER BY f.created_at DESC
            LIMIT %s
            """,
            (limit,),
        )
    )


def can_access(employee_id, customer_id):
    if not employee_id:
        return get(customer_id) is not None
    return get(customer_id, employee_id=employee_id) is not None
