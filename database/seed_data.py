#!/usr/bin/env python3
"""Rebuild FotoInsight with synthetic demo records.

The rows are invented for a student project. They are not Fotographiya's
accounts and must not be described as a real studio's performance.

Usage (from the project folder, after .env is filled in):

    python database/seed_data.py --reset
"""

import argparse
import os
import random
import sys
from datetime import date, datetime, timedelta
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from dotenv import load_dotenv
from werkzeug.security import generate_password_hash

from app.schema import apply_schema, connect_raw

load_dotenv(ROOT / ".env")

FIRST = ["Aarav", "Vivaan", "Aditya", "Ananya", "Diya", "Ishaan", "Myra", "Kabir", "Sara", "Arjun", "Meera", "Rohan", "Kiara", "Neel", "Aisha", "Dev", "Navya", "Rahul", "Pooja", "Kunal", "Sana", "Vikram", "Tara", "Nikhil", "Anika", "Harsh", "Riya", "Omar", "Zara", "Yash"]
LAST = ["Sharma", "Verma", "Mehta", "Kapoor", "Iyer", "Reddy", "Singh", "Joshi", "Nair", "Khan", "Patel", "Das", "Bose", "Malhotra", "Gill", "Chopra", "Banerjee", "Kulkarni"]
CITIES = ["Jaipur", "Udaipur", "Jodhpur", "Delhi", "Mumbai", "Bengaluru", "Goa", "Ahmedabad", "Chandigarh", "Hyderabad", "Kolkata", "Pune", "Lucknow", "Indore"]
VENUES = ["Rose Courtyard", "Lake Pavilion", "Garden Terrace", "Old City Haveli", "Palm Lawns", "Civic Hall", "Studio Atelier", "River House"]

SERVICES = [
    ("Wedding Photography", "wedding", "Full-day wedding coverage with a lead photographer and a second shooter when the package includes one.", "images/services/wedding.jpg", 85000, 1),
    ("Pre-Wedding Photography", "pre-wedding", "A planned session before the wedding, usually in one city and one outfit change.", "images/services/prewedding.jpg", 25000, 2),
    ("Destination Wedding Photography", "destination", "Coverage for a wedding held away from the couple's home city, including travel days in the package.", "images/services/destination.jpg", 150000, 3),
    ("Corporate Photography", "corporate", "Conferences, team days, and brand events with a shot list agreed in advance.", "images/services/corporate.jpg", 40000, 4),
    ("Event Photography", "events", "Private celebrations that are not a full wedding day.", "images/services/event.jpg", 35000, 5),
    ("Birthday Photography", "birthday", "Coverage of a birthday gathering, from arrivals to the cake.", "images/services/birthday.jpg", 15000, 6),
    ("Engagement Photography", "engagement", "The engagement ceremony and a short portrait session.", "images/services/engagement.jpg", 20000, 7),
    ("Cinematography", "film", "A wedding or event film, edited to an agreed length.", "images/services/cinema.jpg", 75000, 8),
    ("Wedding Albums", "albums", "Design and print of a wedding album after the edit is approved.", "images/services/album.jpg", 18000, 9),
    ("Maternity Photography", "portraits", "A studio or outdoor maternity session.", "images/services/maternity.jpg", 18000, 10),
    ("Product Photography", "commercial", "Still photographs of products for a catalogue or launch.", "images/services/product.jpg", 12000, 11),
    ("Reception Coverage", "wedding", "Evening reception coverage when the ceremony is handled separately.", "images/services/reception.jpg", 30000, 12),
]

PACKAGES = [
    (0, "Basic Wedding Package", "One photographer, eight hours, edited photographs.", 85000, "8 hours, 1 photographer, online gallery"),
    (0, "Premium Wedding Package", "Two photographers, full day, and a highlight film handoff to the editor.", 165000, "12 hours, 2 photographers, teaser film"),
    (2, "Destination Wedding Package", "Two travel days plus the wedding day for a lead photographer.", 250000, "Travel, 2 days, lead photographer"),
    (1, "Pre-Wedding Package", "A two-hour session and 40 edited photographs.", 35000, "2 hours, 40 photographs"),
    (3, "Corporate Event Package", "A full conference day with speaker and audience coverage.", 65000, "8 hours, same-week preview"),
    (6, "Engagement Package", "Ceremony plus portraits.", 28000, "4 hours, online gallery"),
    (5, "Birthday Package", "Three hours at the venue.", 18000, "3 hours, 60 photographs"),
    (7, "Wedding Film Package", "Ceremony, speeches, and a 3 to 5 minute film.", 120000, "Film crew, licensed music edit"),
]

EMPLOYEES = [
    ("Anika Rao", "anika.rao@fotoinsight.demo", "9800000001", "Lead Photographer", "Jaipur"),
    ("Kabir Sethi", "kabir.sethi@fotoinsight.demo", "9800000002", "Photographer", "Delhi"),
    ("Meera Iyer", "meera.iyer@fotoinsight.demo", "9800000003", "Photographer", "Udaipur"),
    ("Rohan Das", "rohan.das@fotoinsight.demo", "9800000004", "Cinematographer", "Mumbai"),
    ("Sara Khan", "sara.khan@fotoinsight.demo", "9800000005", "Cinematographer", "Goa"),
    ("Dev Malhotra", "dev.malhotra@fotoinsight.demo", "9800000006", "Editor", "Jaipur"),
    ("Tara Nair", "tara.nair@fotoinsight.demo", "9800000007", "Editor", "Bengaluru"),
    ("Neel Kapoor", "neel.kapoor@fotoinsight.demo", "9800000008", "Coordinator", "Jaipur"),
]

EVENT_WEIGHTS = [0.34, 0.12, 0.1, 0.08, 0.07, 0.06, 0.08, 0.07, 0.04, 0.02, 0.01, 0.01]
OPEN_STATUSES = ["new", "contacted", "follow_up", "negotiation", "rejected"]
OPEN_WEIGHTS = [0.22, 0.24, 0.16, 0.14, 0.24]
COMMENTS = [
    "The plan was easy to follow and the team was where they said they would be.",
    "We received a clear schedule and the edit arrived on the agreed week.",
    "The photographs felt like the day, not like a set.",
    "Communication before the event was calm and specific.",
    "The film matched the length we had asked for.",
]


def money(value):
    return Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def weighted_date(rng, start, end):
    peak = {11, 12, 1, 2}
    span = (end - start).days
    choice = start
    for _ in range(12):
        choice = start + timedelta(days=rng.randint(0, span))
        if choice.month in peak or rng.random() < 0.28:
            return choice
    return choice


def main():
    parser = argparse.ArgumentParser(description="Load synthetic FotoInsight demo data")
    parser.add_argument("--reset", action="store_true", help="Drop and recreate every table, then load demo rows")
    args = parser.parse_args()
    if not args.reset:
        raise SystemExit("Refusing to continue without --reset. This script deletes the current FotoInsight tables.")

    db_path = os.environ.get(
        "SQLITE_PATH",
        str(ROOT / "instance" / "fotoinsight.db"),
    )
    if Path(db_path).name.endswith("_test.db") or "test" in Path(db_path).stem:
        raise SystemExit("Refusing to seed the test database.")

    connection = connect_raw(db_path)
    rng = random.Random(42)
    apply_schema(connection)
    with connection.cursor() as cur:
        _seed(cur, rng)
    connection.commit()
    connection.close()
    print(f"Demo data loaded into {db_path}")
    print("Log in at /admin/login")
    print("Admin username: admin    password: Admin@123")
    print("Employee username: employee    password: Employee@123")
    print("All business rows are marked is_demo = 1 and are synthetic.")


def _seed(cur, rng):
    cur.execute(
        """
        UPDATE business_settings SET
            business_name=%s, tagline=%s, email=%s, phone=%s, address=%s, city=%s,
            about_intro=%s, mission=%s, vision=%s
        WHERE id=1
        """,
        (
            "FotoInsight Studio",
            "Wedding, celebration, and film — planned with care.",
            "hello@fotoinsight.demo",
            "+91 00000 00000",
            "Sample Studio Address, C-Scheme",
            "Jaipur",
            "FotoInsight Studio plans, photographs, and delivers weddings, pre-wedding sessions, corporate events, and private celebrations. This text is sample copy for the demonstration site.",
            "To give every client a clear path from the first enquiry to the delivered film and album.",
            "A studio day that stays organised because the team, the date, and the balance were agreed before the event.",
        ),
    )
    employee_ids = []
    for name, email, phone, title, city in EMPLOYEES:
        cur.execute(
            """
            INSERT INTO employees (full_name, email, phone, job_title, city, status, is_demo)
            VALUES (%s,%s,%s,%s,%s,'active',1)
            """,
            (name, email, phone, title, city),
        )
        employee_ids.append(cur.lastrowid)
    photographers = employee_ids[0:3]
    films = employee_ids[3:5]
    editors = employee_ids[5:7]
    cur.execute(
        """
        INSERT INTO users (username, email, password_hash, role, employee_id, display_name)
        VALUES (%s,%s,%s,'admin',NULL,%s)
        """,
        ("admin", "admin@fotoinsight.demo", generate_password_hash("Admin@123"), "Studio Admin"),
    )
    admin_id = cur.lastrowid
    cur.execute(
        """
        INSERT INTO users (username, email, password_hash, role, employee_id, display_name)
        VALUES (%s,%s,%s,'employee',%s,%s)
        """,
        ("employee", EMPLOYEES[0][1], generate_password_hash("Employee@123"), employee_ids[0], EMPLOYEES[0][0]),
    )

    service_ids = []
    for name, category, description, image, price, order in SERVICES:
        slug = name.lower().replace(" ", "-")
        cur.execute(
            """
            INSERT INTO services (name, slug, category, description, image_path, base_price, status, sort_order, is_demo)
            VALUES (%s,%s,%s,%s,%s,%s,'active',%s,1)
            """,
            (name, slug, category, description, image, money(price), order),
        )
        service_ids.append(cur.lastrowid)
    package_ids = []
    packages_by_service = {service_id: [] for service_id in service_ids}
    for index, name, description, price, inclusions in PACKAGES:
        service_id = service_ids[index]
        cur.execute(
            """
            INSERT INTO packages (service_id, name, description, price, inclusions, status, is_demo)
            VALUES (%s,%s,%s,%s,%s,'active',1)
            """,
            (service_id, name, description, money(price), inclusions),
        )
        package_id = cur.lastrowid
        package_ids.append(package_id)
        packages_by_service[service_id].append((package_id, money(price)))

    today = date.today()
    customer_ids = []
    for number in range(1, 221):
        full_name = f"{rng.choice(FIRST)} {rng.choice(LAST)}"
        city = rng.choice(CITIES)
        registered = weighted_date(rng, date(2023, 1, 5), today)
        cur.execute(
            """
            INSERT INTO customers (full_name, email, phone, city, address, registration_date, is_demo, created_at)
            VALUES (%s,%s,%s,%s,%s,%s,1,%s)
            """,
            (
                full_name,
                f"guest{number}@example.demo",
                f"9{rng.randint(100000000, 999999999)}",
                city,
                f"{rng.randint(1, 180)}, Sample Lane",
                registered,
                datetime.combine(registered, datetime.min.time()),
            ),
        )
        customer_ids.append(cur.lastrowid)

    # 155 customers will hold 170 bookings: 140 once, 15 twice.
    repeaters = customer_ids[:15]
    singles = customer_ids[15:155]
    booking_customers = singles + repeaters + repeaters
    rng.shuffle(booking_customers)

    enquiry_rows = []
    for number in range(1, 341):
        service_index = rng.choices(range(len(service_ids)), weights=EVENT_WEIGHTS, k=1)[0]
        service_id = service_ids[service_index]
        event_type = SERVICES[service_index][0]
        event_day = weighted_date(rng, date(2023, 2, 1), date(2027, 2, 20))
        created_day = event_day - timedelta(days=rng.randint(20, 120))
        if created_day < date(2023, 1, 3):
            created_day = date(2023, 1, 3)
        if created_day > today:
            created_day = today - timedelta(days=rng.randint(1, 20))
        city = rng.choice(CITIES)
        package = rng.choice(packages_by_service[service_id]) if packages_by_service[service_id] and rng.random() < 0.7 else None
        budget = package[1] if package else money(SERVICES[service_index][4] * rng.uniform(0.9, 1.4))
        enquiry_rows.append({
            "service_id": service_id,
            "event_type": event_type,
            "event_day": event_day,
            "created_day": created_day,
            "city": city,
            "package_id": package[0] if package else None,
            "budget": money(budget),
            "base_price": money(SERVICES[service_index][4]),
        })

    converted_indexes = list(range(170))
    for index, row in enumerate(enquiry_rows):
        customer_id = booking_customers[index] if index < 170 else rng.choice(customer_ids)
        status = "converted" if index in converted_indexes else rng.choices(OPEN_STATUSES, weights=OPEN_WEIGHTS, k=1)[0]
        assigned = rng.choice(employee_ids) if status != "new" or rng.random() < 0.35 else None
        if index < 25:
            assigned = employee_ids[0]
        person = customer_id
        cur.execute("SELECT full_name, email, phone, city FROM customers WHERE id=%s", (person,))
        person = cur.fetchone()
        cur.execute(
            """
            INSERT INTO enquiries (
                enquiry_code, customer_id, full_name, email, phone, event_type, event_date, event_location,
                city, guest_count, package_id, estimated_budget, requirements, status, assigned_employee_id,
                submission_token, source, is_demo, created_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s)
            """,
            (
                f"ENQ-{index + 1:05d}",
                customer_id if status == "converted" or rng.random() < 0.45 else None,
                person["full_name"],
                person["email"],
                person["phone"],
                row["event_type"],
                row["event_day"],
                f"{rng.choice(VENUES)}, {row['city']}",
                row["city"],
                rng.choice([40, 80, 120, 180, 250, 400, None]),
                row["package_id"],
                row["budget"],
                "Demo enquiry generated for the student project.",
                status,
                assigned,
                f"demo-token-{index + 1}",
                "website" if index % 4 else "admin",
                datetime.combine(row["created_day"], datetime.min.time()) + timedelta(hours=rng.randint(9, 18)),
            ),
        )
        enquiry_id = cur.lastrowid
        row["enquiry_id"] = enquiry_id
        row["customer_id"] = customer_id
        row["status"] = status
        if index < 40:
            cur.execute(
                "INSERT INTO enquiry_notes (enquiry_id, user_id, note) VALUES (%s,%s,%s)",
                (enquiry_id, admin_id, "Demo note: confirm the venue entrance and the family timeline."),
            )

    booking_ids = []
    for index in range(170):
        row = enquiry_rows[index]
        total = row["budget"] if row["budget"] and row["budget"] > 0 else row["base_price"]
        if row["event_day"] < today - timedelta(days=14):
            status = rng.choices(["completed", "completed", "cancelled", "in_progress"], weights=[0.72, 0.1, 0.1, 0.08], k=1)[0]
        elif row["event_day"] <= today + timedelta(days=21):
            status = rng.choice(["confirmed", "in_progress", "on_hold"])
        else:
            status = rng.choices(["confirmed", "on_hold"], weights=[0.85, 0.15], k=1)[0]
        booked_on = row["created_day"] + timedelta(days=rng.randint(2, 18))
        if booked_on > today:
            booked_on = today - timedelta(days=1)
        if booked_on < row["created_day"]:
            booked_on = row["created_day"]
        cur.execute(
            """
            INSERT INTO bookings (
                booking_code, customer_id, enquiry_id, service_id, package_id, event_name, event_type,
                event_date, event_location, city, total_amount, status, notes, is_demo, created_at
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,1,%s)
            """,
            (
                f"BKG-{index + 1:05d}",
                row["customer_id"],
                row["enquiry_id"],
                row["service_id"],
                row["package_id"],
                f"{row['event_type']} — demo {index + 1}",
                row["event_type"],
                row["event_day"],
                f"{rng.choice(VENUES)}, {row['city']}",
                row["city"],
                total,
                status,
                "Synthetic booking. The contract amount is not revenue until payments are recorded.",
                datetime.combine(booked_on, datetime.min.time()) + timedelta(hours=11),
            ),
        )
        booking_id = cur.lastrowid
        booking_ids.append(booking_id)
        lead = photographers[index % len(photographers)]
        cur.execute(
            "INSERT INTO booking_team (booking_id, employee_id, team_role, is_lead) VALUES (%s,%s,%s,1)",
            (booking_id, lead, "Lead Photographer"),
        )
        if rng.random() < 0.45:
            cur.execute(
                "INSERT INTO booking_team (booking_id, employee_id, team_role, is_lead) VALUES (%s,%s,%s,0)",
                (booking_id, films[index % len(films)], "Cinematographer"),
            )
        _payments(cur, rng, booking_id, total, status, booked_on, row["event_day"], admin_id, today)

    project_count = 0
    for index, booking_id in enumerate(booking_ids):
        if project_count >= 80:
            break
        row = enquiry_rows[index]
        if row["event_day"] > today + timedelta(days=60) and rng.random() < 0.7:
            continue
        start = row["event_day"]
        delivery = row["event_day"] + timedelta(days=rng.choice([14, 21, 30, 45]))
        if row["event_day"] < today - timedelta(days=40):
            status = rng.choice(["delivered", "completed", "completed"])
        elif row["event_day"] < today:
            status = rng.choice(["editing", "review", "in_progress", "completed"])
        else:
            status = rng.choice(["not_started", "in_progress"])
        if project_count < 8 and delivery < today:
            status = "editing"
        cur.execute(
            """
            INSERT INTO projects (
                project_code, booking_id, photographer_id, editor_id, start_date, delivery_date, status, notes, is_demo
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,1)
            """,
            (
                f"PRJ-{project_count + 1:05d}",
                booking_id,
                photographers[index % len(photographers)],
                editors[index % len(editors)],
                start,
                delivery,
                status,
                "Demo project for delivery tracking.",
            ),
        )
        project_count += 1

    for index in range(12):
        cur.execute(
            """
            INSERT INTO customer_feedback (customer_id, booking_id, rating, comment, is_public, is_demo)
            VALUES (%s,%s,%s,%s,1,1)
            """,
            (booking_customers[index], booking_ids[index], rng.choice([4, 5, 5]), COMMENTS[index % len(COMMENTS)]),
        )

    cur.execute("SELECT COUNT(*) AS n FROM customers")
    customers = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM enquiries")
    enquiries = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM bookings")
    bookings = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM payments")
    payments = cur.fetchone()["n"]
    cur.execute("SELECT COUNT(*) AS n FROM projects")
    projects = cur.fetchone()["n"]
    print(f"Customers {customers}, enquiries {enquiries}, bookings {bookings}, payments {payments}, projects {projects}")


def _payments(cur, rng, booking_id, total, status, booked_on, event_day, admin_id, today):
    total = money(total)

    def add(amount, pay_day, pay_status, method):
        amount = money(amount)
        if amount <= 0:
            return
        if pay_day > today and pay_status != "pending":
            pay_day = today
        cur.execute(
            """
            INSERT INTO payments (
                payment_code, booking_id, amount, payment_date, method, transaction_ref, status, notes, recorded_by, is_demo
            ) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,1)
            """,
            (
                f"PAY-{booking_id}-{pay_status[:3]}-{rng.randint(100,999)}",
                booking_id,
                amount,
                pay_day,
                method,
                f"DEMO{booking_id}{rng.randint(1000,9999)}",
                pay_status,
                "Synthetic payment. Pending rows are not revenue.",
                admin_id,
            ),
        )

    advance = money(total * Decimal(str(rng.uniform(0.3, 0.5))))
    if status == "cancelled":
        if rng.random() < 0.6:
            add(advance, booked_on + timedelta(days=1), "paid", "upi")
            add(advance, booked_on + timedelta(days=10), "refunded", "bank_transfer")
        return
    roll = rng.random()
    if event_day > today:
        if roll < 0.7:
            add(advance, booked_on + timedelta(days=2), "paid", rng.choice(["upi", "bank_transfer", "card"]))
        elif roll < 0.85:
            add(total, booked_on + timedelta(days=2), "paid", "upi")
        elif roll < 0.93:
            add(money(total * Decimal("0.2")), booked_on + timedelta(days=3), "pending", "upi")
        return
    if roll < 0.62:
        add(advance, booked_on + timedelta(days=1), "paid", "upi")
        rest = money(total - advance)
        add(rest, min(event_day + timedelta(days=7), today), "paid", "bank_transfer")
    elif roll < 0.8:
        add(advance, booked_on + timedelta(days=1), "partially_paid", "cash")
    elif roll < 0.93:
        add(total, booked_on + timedelta(days=4), "paid", "card")
    else:
        add(total, booked_on + timedelta(days=4), "paid", "upi")
        add(money(total * Decimal("0.1")), min(event_day + timedelta(days=20), today), "refunded", "bank_transfer")


if __name__ == "__main__":
    main()
