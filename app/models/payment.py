"""Payments. Revenue is the sum of collected rows, not the booking contract."""

import uuid
from decimal import Decimal

from app.db import execute, query_all, query_one, transaction, tx_execute, tx_query_one
from app.errors import AppError
from app.utils import clean_row, clean_rows, code_for, like, pagination


def _signed_case(alias="p"):
    return f"""
        CASE
            WHEN {alias}.status IN ('paid', 'partially_paid') THEN {alias}.amount
            WHEN {alias}.status = 'refunded' THEN -{alias}.amount
            ELSE 0
        END
    """


def collected_for(booking_id, exclude_id=None, db=None):
    sql = f"SELECT COALESCE(SUM({_signed_case()}), 0) AS received FROM payments p WHERE p.booking_id=%s"
    params = [booking_id]
    if exclude_id:
        sql += " AND p.id <> %s"
        params.append(exclude_id)
    row = tx_query_one(db, sql, params) if db is not None else query_one(sql, params)
    return Decimal(str(row["received"] or 0)).quantize(Decimal("0.01"))


def _check_effect(total, base_received, amount, status):
    if status in ("paid", "partially_paid"):
        new_received = base_received + amount
    elif status == "refunded":
        new_received = base_received - amount
    else:
        new_received = base_received
        if amount > (total - base_received) + Decimal("0.009"):
            raise AppError("A pending amount cannot be larger than the outstanding balance.")
    if new_received < 0:
        raise AppError(
            "This refund is larger than the other payments already collected. "
            "Keep the original receipt and add a separate refund row.",
            409,
        )
    if new_received - total > Decimal("0.009"):
        outstanding = total - base_received
        raise AppError(
            f"Only INR {outstanding} is still outstanding on this booking. "
            "The full contract is not recorded as paid until the money arrives.",
            409,
        )


def list_payments(q="", status="", method="", date_from=None, date_to=None, page=1, per_page=10):
    where = ["1=1"]
    params = []
    if q:
        pattern = like(q)
        where.append("(pay.payment_code LIKE %s ESCAPE '\\\\' OR c.full_name LIKE %s ESCAPE '\\\\' OR b.booking_code LIKE %s ESCAPE '\\\\' OR pay.transaction_ref LIKE %s ESCAPE '\\\\')")
        params.extend([pattern, pattern, pattern, pattern])
    if status:
        where.append("pay.status = %s")
        params.append(status)
    if method:
        where.append("pay.method = %s")
        params.append(method)
    if date_from:
        where.append("pay.payment_date >= %s")
        params.append(date_from)
    if date_to:
        where.append("pay.payment_date <= %s")
        params.append(date_to)
    base = f"""
        FROM payments pay
        JOIN bookings b ON b.id = pay.booking_id
        JOIN customers c ON c.id = b.customer_id
        WHERE {' AND '.join(where)}
    """
    total = query_one(f"SELECT COUNT(*) AS n {base}", params)["n"]
    page_info = pagination(total, page, per_page)
    rows = query_all(
        f"""
        SELECT pay.*, b.booking_code, b.total_amount, b.event_name, c.full_name AS customer_name,
               (SELECT COALESCE(SUM({_signed_case('p2')}), 0) FROM payments p2 WHERE p2.booking_id = b.id) AS booking_received
        {base}
        ORDER BY pay.payment_date DESC, pay.id DESC
        LIMIT %s OFFSET %s
        """,
        params + [page_info["per_page"], page_info["offset"]],
    )
    cleaned = []
    for row in clean_rows(rows):
        row["outstanding"] = round(row["total_amount"] - row["booking_received"], 2)
        cleaned.append(row)
    return cleaned, page_info


def get(payment_id):
    return clean_row(
        query_one(
            """
            SELECT pay.*, b.booking_code, b.total_amount, c.full_name AS customer_name
            FROM payments pay
            JOIN bookings b ON b.id = pay.booking_id
            JOIN customers c ON c.id = b.customer_id
            WHERE pay.id=%s
            """,
            (payment_id,),
        )
    )


def create(data, user_id=None, is_demo=0):
    with transaction() as db:
        booking = tx_query_one(db, "SELECT id, total_amount, is_demo FROM bookings WHERE id=%s FOR UPDATE", (data["booking_id"],))
        if not booking:
            raise AppError("Booking not found.", 404)
        amount = Decimal(str(data["amount"])).quantize(Decimal("0.01"))
        base = collected_for(booking["id"], db=db)
        _check_effect(Decimal(str(booking["total_amount"])), base, amount, data["status"])
        payment_id = tx_execute(
            db,
            """
            INSERT INTO payments (
                payment_code, booking_id, amount, payment_date, method, transaction_ref, status, notes, recorded_by, is_demo
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                f"TMP-{uuid.uuid4().hex[:12]}",
                booking["id"],
                amount,
                data["payment_date"],
                data["method"],
                data.get("transaction_ref"),
                data["status"],
                data.get("notes"),
                user_id,
                is_demo,
            ),
        )
        code = code_for("PAY", payment_id)
        tx_execute(db, "UPDATE payments SET payment_code=%s WHERE id=%s", (code, payment_id))
        return {"id": payment_id, "payment_code": code}


def update(payment_id, data):
    with transaction() as db:
        current = tx_query_one(db, "SELECT * FROM payments WHERE id=%s FOR UPDATE", (payment_id,))
        if not current:
            raise AppError("Payment not found.", 404)
        booking = tx_query_one(db, "SELECT * FROM bookings WHERE id=%s FOR UPDATE", (data["booking_id"],))
        if not booking:
            raise AppError("Booking not found.", 404)
        amount = Decimal(str(data["amount"])).quantize(Decimal("0.01"))
        base = collected_for(booking["id"], exclude_id=payment_id, db=db)
        _check_effect(Decimal(str(booking["total_amount"])), base, amount, data["status"])
        tx_execute(
            db,
            """
            UPDATE payments SET
                booking_id=%s, amount=%s, payment_date=%s, method=%s, transaction_ref=%s, status=%s, notes=%s
            WHERE id=%s
            """,
            (
                data["booking_id"], amount, data["payment_date"], data["method"],
                data.get("transaction_ref"), data["status"], data.get("notes"), payment_id,
            ),
        )


def delete(payment_id):
    if not get(payment_id):
        raise AppError("Payment not found.", 404)
    execute("DELETE FROM payments WHERE id=%s", (payment_id,))


def summary():
    """Studio-wide collection totals. Pending money is reported separately and is not revenue."""
    row = query_one(
        f"""
        SELECT
            COALESCE(SUM(CASE WHEN status IN ('paid','partially_paid') THEN amount ELSE 0 END), 0) AS collected,
            COALESCE(SUM(CASE WHEN status='refunded' THEN amount ELSE 0 END), 0) AS refunds,
            COALESCE(SUM(CASE WHEN status='pending' THEN amount ELSE 0 END), 0) AS pending,
            COALESCE(SUM({_signed_case()}), 0) AS net_revenue
        FROM payments p
        """
    )
    contracts = query_one("SELECT COALESCE(SUM(total_amount), 0) AS contracts FROM bookings WHERE status <> 'cancelled'")
    net = Decimal(str(row["net_revenue"] or 0))
    contract = Decimal(str(contracts["contracts"] or 0))
    return clean_row({
        "collected": row["collected"],
        "refunds": row["refunds"],
        "pending_not_revenue": row["pending"],
        "net_revenue": net,
        "contract_value": contract,
        "outstanding": contract - net,
    })
