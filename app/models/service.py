"""Photography services and the packages sold under them."""

from pymysql.err import IntegrityError

from app.db import execute, query_all, query_one
from app.errors import AppError
from app.utils import clean_row, clean_rows, slugify


def list_services(active_only=False):
    sql = "SELECT * FROM services"
    if active_only:
        sql += " WHERE status = 'active'"
    sql += " ORDER BY sort_order, name"
    services = clean_rows(query_all(sql))
    packages = clean_rows(query_all("SELECT * FROM packages ORDER BY price"))
    grouped = {}
    for package in packages:
        grouped.setdefault(package["service_id"], []).append(package)
    for service in services:
        service["packages"] = grouped.get(service["id"], [])
    return services


def get(service_id):
    row = clean_row(query_one("SELECT * FROM services WHERE id=%s", (service_id,)))
    if not row:
        return None
    row["packages"] = clean_rows(query_all("SELECT * FROM packages WHERE service_id=%s ORDER BY price", (service_id,)))
    return row


def get_by_name(name):
    return clean_row(query_one("SELECT * FROM services WHERE name=%s", (name,)))


def create(data, is_demo=0):
    slug = slugify(data["name"])
    base = slug
    counter = 2
    while query_one("SELECT id FROM services WHERE slug=%s", (slug,)):
        slug = f"{base}-{counter}"
        counter += 1
    try:
        return execute(
            """
            INSERT INTO services (name, slug, category, description, image_path, base_price, status, sort_order, is_demo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """,
            (
                data["name"], slug, data["category"], data["description"], data.get("image_path"),
                data["base_price"], data["status"], data.get("sort_order") or 0, is_demo,
            ),
        )
    except IntegrityError as exc:
        raise AppError("A service with that name already exists.", 409) from exc


def update(service_id, data):
    current = get(service_id)
    if not current:
        raise AppError("Service not found.", 404)
    slug = slugify(data["name"])
    if slug != current["slug"] and query_one("SELECT id FROM services WHERE slug=%s AND id<>%s", (slug, service_id)):
        slug = f"{slug}-{service_id}"
    try:
        execute(
            """
            UPDATE services
            SET name=%s, slug=%s, category=%s, description=%s, base_price=%s, status=%s, sort_order=%s
            WHERE id=%s
            """,
            (data["name"], slug, data["category"], data["description"], data["base_price"], data["status"], data.get("sort_order") or 0, service_id),
        )
    except IntegrityError as exc:
        raise AppError("A service with that name already exists.", 409) from exc


def set_image(service_id, image_path):
    if not get(service_id):
        raise AppError("Service not found.", 404)
    execute("UPDATE services SET image_path=%s WHERE id=%s", (image_path, service_id))


def set_status(service_id, status):
    if status not in ("active", "inactive"):
        raise AppError("Status must be active or inactive.")
    if not get(service_id):
        raise AppError("Service not found.", 404)
    execute("UPDATE services SET status=%s WHERE id=%s", (status, service_id))


def delete(service_id):
    if not get(service_id):
        raise AppError("Service not found.", 404)
    used = query_one("SELECT COUNT(*) AS n FROM bookings WHERE service_id=%s", (service_id,))["n"]
    if used:
        raise AppError("This service is used by bookings. Deactivate it instead of deleting it.", 409)
    packages = query_one(
        """
        SELECT COUNT(*) AS n FROM enquiries e
        JOIN packages p ON p.id = e.package_id
        WHERE p.service_id=%s
        """,
        (service_id,),
    )["n"]
    if packages:
        raise AppError("This service has packages linked to enquiries. Deactivate it instead.", 409)
    execute("DELETE FROM packages WHERE service_id=%s", (service_id,))
    execute("DELETE FROM services WHERE id=%s", (service_id,))


def list_packages(active_only=False):
    sql = """
        SELECT p.*, s.name AS service_name
        FROM packages p
        JOIN services s ON s.id = p.service_id
    """
    if active_only:
        sql += " WHERE p.status = 'active' AND s.status = 'active'"
    sql += " ORDER BY s.sort_order, p.price"
    return clean_rows(query_all(sql))


def get_package(package_id):
    return clean_row(
        query_one(
            """
            SELECT p.*, s.name AS service_name
            FROM packages p JOIN services s ON s.id = p.service_id
            WHERE p.id=%s
            """,
            (package_id,),
        )
    )


def create_package(data, is_demo=0):
    if not get(data["service_id"]):
        raise AppError("Choose a valid service.", 404)
    return execute(
        """
        INSERT INTO packages (service_id, name, description, price, inclusions, status, is_demo)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        (data["service_id"], data["name"], data["description"], data["price"], data["inclusions"], data["status"], is_demo),
    )


def update_package(package_id, data):
    if not get_package(package_id):
        raise AppError("Package not found.", 404)
    if not get(data["service_id"]):
        raise AppError("Choose a valid service.", 404)
    execute(
        """
        UPDATE packages
        SET service_id=%s, name=%s, description=%s, price=%s, inclusions=%s, status=%s
        WHERE id=%s
        """,
        (data["service_id"], data["name"], data["description"], data["price"], data["inclusions"], data["status"], package_id),
    )


def delete_package(package_id):
    if not get_package(package_id):
        raise AppError("Package not found.", 404)
    used_bookings = query_one("SELECT COUNT(*) AS n FROM bookings WHERE package_id=%s", (package_id,))["n"]
    used_enquiries = query_one("SELECT COUNT(*) AS n FROM enquiries WHERE package_id=%s", (package_id,))["n"]
    if used_bookings or used_enquiries:
        raise AppError("This package is already used. Deactivate it instead of deleting it.", 409)
    execute("DELETE FROM packages WHERE id=%s", (package_id,))
