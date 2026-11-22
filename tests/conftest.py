"""Fresh SQLite test database for each test."""

import sys
from pathlib import Path

import pytest
from werkzeug.security import generate_password_hash

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app import create_app
from app.config import TestConfig
from app.schema import apply_schema, connect_raw


@pytest.fixture
def app():
    db_path = Path(TestConfig.SQLITE_PATH)
    if db_path.exists():
        db_path.unlink()
    application = create_app(TestConfig)
    connection = connect_raw(db_path)
    apply_schema(connection)
    with connection.cursor() as cur:
        cur.execute(
            """
            INSERT INTO employees (full_name, email, phone, job_title, city, status)
            VALUES ('Anika Rao','anika@example.demo','9800000001','Photographer','Jaipur','active')
            """
        )
        employee_id = cur.lastrowid
        cur.execute(
            """
            INSERT INTO users (username, email, password_hash, role, display_name)
            VALUES ('admin','admin@example.demo',%s,'admin','Studio Admin')
            """,
            (generate_password_hash("Admin@123"),),
        )
        cur.execute(
            """
            INSERT INTO users (username, email, password_hash, role, employee_id, display_name)
            VALUES ('employee','anika@example.demo',%s,'employee',%s,'Anika Rao')
            """,
            (generate_password_hash("Employee@123"), employee_id),
        )
        cur.execute(
            """
            INSERT INTO services (name, slug, category, description, base_price, status, sort_order)
            VALUES ('Wedding Photography','wedding-photography','wedding','Test service',85000,'active',1)
            """
        )
        service_id = cur.lastrowid
        cur.execute(
            """
            INSERT INTO packages (service_id, name, description, price, status)
            VALUES (%s,'Basic Wedding Package','Test package',90000,'active')
            """,
            (service_id,),
        )
    connection.commit()
    connection.close()
    yield application
    if db_path.exists():
        db_path.unlink()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def admin(app):
    return _login(app.test_client(), "admin", "Admin@123")


@pytest.fixture
def employee(app):
    return _login(app.test_client(), "employee", "Employee@123")


def _login(client, username, password):
    client.get("/admin/login")
    with client.session_transaction() as sess:
        token = sess["csrf"]
    response = client.post(
        "/api/auth/login",
        json={"username": username, "password": password},
        headers={"X-CSRF-Token": token, "X-Requested-With": "fetch"},
    )
    assert response.status_code == 200, response.get_json()
    with client.session_transaction() as sess:
        token = sess["csrf"]
    client.csrf = token
    return client
