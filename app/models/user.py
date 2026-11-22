"""Login accounts. Passwords are stored only as Werkzeug hashes."""

from werkzeug.security import check_password_hash, generate_password_hash

from app.db import execute, query_one
from app.errors import AppError
from app.utils import clean_row


def authenticate(username, password):
    if not username or not password:
        return None
    row = query_one(
        """
        SELECT id, username, email, password_hash, role, employee_id, display_name, is_active
        FROM users
        WHERE username = %s
        """,
        (username.strip(),),
    )
    if not row or not row["is_active"]:
        return None
    if not check_password_hash(row["password_hash"], password):
        return None
    row.pop("password_hash", None)
    return clean_row(row)


def get(user_id):
    return clean_row(
        query_one(
            """
            SELECT id, username, email, role, employee_id, display_name, is_active
            FROM users WHERE id = %s
            """,
            (user_id,),
        )
    )


def set_password(user_id, new_password):
    execute(
        "UPDATE users SET password_hash = %s WHERE id = %s",
        (generate_password_hash(new_password), user_id),
    )


def create_login(employee, username, password, role):
    existing = query_one("SELECT id FROM users WHERE username = %s OR email = %s", (username, employee["email"]))
    if existing:
        raise AppError("That username or email already has a login.", 409)
    if role not in ("admin", "employee"):
        raise AppError("Role must be admin or employee.")
    user_id = execute(
        """
        INSERT INTO users (username, email, password_hash, role, employee_id, display_name, is_active)
        VALUES (%s, %s, %s, %s, %s, %s, 1)
        """,
        (
            username.strip(),
            employee["email"],
            generate_password_hash(password),
            role,
            employee["id"],
            employee["full_name"],
        ),
    )
    return user_id


def by_employee(employee_id):
    return clean_row(
        query_one(
            "SELECT id, username, role, is_active FROM users WHERE employee_id = %s",
            (employee_id,),
        )
    )
