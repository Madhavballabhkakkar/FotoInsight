"""Studio staff. A staff record is not a login until an admin creates one."""

from app.db import execute, query_all, query_one
from app.errors import AppError
from app.utils import clean_row, clean_rows


def list_employees(include_inactive=True):
    sql = "SELECT * FROM employees"
    if not include_inactive:
        sql += " WHERE status = 'active'"
    sql += " ORDER BY full_name"
    return clean_rows(query_all(sql))


def get(employee_id):
    return clean_row(query_one("SELECT * FROM employees WHERE id = %s", (employee_id,)))


def create(data, is_demo=0):
    return execute(
        """
        INSERT INTO employees (full_name, email, phone, job_title, city, status, is_demo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (data["full_name"], data["email"], data["phone"], data["job_title"], data["city"], data["status"], is_demo),
    )


def update(employee_id, data):
    if not get(employee_id):
        raise AppError("Employee not found.", 404)
    execute(
        """
        UPDATE employees
        SET full_name=%s, email=%s, phone=%s, job_title=%s, city=%s, status=%s
        WHERE id=%s
        """,
        (data["full_name"], data["email"], data["phone"], data["job_title"], data["city"], data["status"], employee_id),
    )


def active_choices():
    return clean_rows(query_all("SELECT id, full_name, job_title FROM employees WHERE status='active' ORDER BY full_name"))
