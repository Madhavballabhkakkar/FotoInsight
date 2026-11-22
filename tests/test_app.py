"""Functional checks for login, records, money, analytics, and reports."""

from datetime import date, timedelta

def auth(client, method, url, **kwargs):
    headers = kwargs.pop("headers", {})
    headers["X-CSRF-Token"] = client.csrf
    headers["X-Requested-With"] = "fetch"
    return client.open(url, method=method, headers=headers, **kwargs)


def test_login_logout_and_locked_pages(client):
    assert client.get("/admin/customers", follow_redirects=False).status_code == 302
    bad = client.get("/admin/login")
    with client.session_transaction() as sess:
        token = sess["csrf"]
    failed = client.post("/api/auth/login", json={"username": "admin", "password": "wrong"}, headers={"X-CSRF-Token": token})
    assert failed.status_code == 401
    client.get("/admin/login")
    with client.session_transaction() as sess:
        token = sess["csrf"]
    ok = client.post("/api/auth/login", json={"username": "admin", "password": "Admin@123"}, headers={"X-CSRF-Token": token})
    assert ok.status_code == 200
    with client.session_transaction() as sess:
        token = sess["csrf"]
    logged_out = client.post("/admin/logout", data={"csrf_token": token}, follow_redirects=False)
    assert logged_out.status_code == 302
    assert client.get("/api/customers").status_code == 401


def test_public_pages_and_duplicate_enquiry(client):
    assert client.get("/").status_code == 200
    assert client.get("/services").status_code == 200
    assert client.get("/portfolio").status_code == 200
    page = client.get("/enquiry")
    assert page.status_code == 200
    with client.session_transaction() as sess:
        token = sess["csrf"]
    payload = {
        "full_name": "Riya Sharma",
        "email": "riya@example.demo",
        "phone": "9811111111",
        "event_type": "Wedding Photography",
        "event_date": "2026-12-12",
        "event_location": "Rose Courtyard",
        "city": "Jaipur",
        "guest_count": "120",
        "estimated_budget": "90000",
        "requirements": "Evening ceremony",
        "submission_token": "tokenenquiry01",
    }
    headers = {"X-CSRF-Token": token, "X-Requested-With": "fetch"}
    first = client.post("/api/public/enquiries", json=payload, headers=headers)
    second = client.post("/api/public/enquiries", json=payload, headers=headers)
    assert first.status_code == 201
    assert second.status_code == 200
    assert second.get_json()["duplicate"] is True
    assert first.get_json()["enquiry_code"] == second.get_json()["enquiry_code"]
    bad = client.post("/api/public/enquiries", json={"full_name": "A"}, headers=headers)
    assert bad.status_code == 400


def test_customer_enquiry_booking_crud(admin):
    created = auth(admin, "POST", "/api/customers", json={
        "full_name": "Aarav Mehta",
        "email": "aarav@example.demo",
        "phone": "9822222222",
        "city": "Udaipur",
        "registration_date": "2026-01-15",
    })
    assert created.status_code == 201
    customer_id = created.get_json()["id"]
    listed = auth(admin, "GET", "/api/customers?q=Aarav")
    assert listed.get_json()["pagination"]["total"] == 1
    updated = auth(admin, "PUT", f"/api/customers/{customer_id}", json={
        "full_name": "Aarav Mehta",
        "email": "aarav@example.demo",
        "phone": "9822222222",
        "city": "Jaipur",
        "registration_date": "2026-01-15",
    })
    assert updated.status_code == 200

    enquiry = auth(admin, "POST", "/api/enquiries", json={
        "full_name": "Aarav Mehta",
        "email": "aarav@example.demo",
        "phone": "9822222222",
        "event_type": "Wedding Photography",
        "event_date": "2026-12-18",
        "event_location": "Lake Pavilion",
        "city": "Udaipur",
        "status": "negotiation",
    })
    assert enquiry.status_code == 201
    enquiry_id = enquiry.get_json()["id"]
    note = auth(admin, "POST", f"/api/enquiries/{enquiry_id}/notes", json={"note": "Called the family."})
    assert note.status_code == 200
    converted = auth(admin, "POST", f"/api/enquiries/{enquiry_id}/convert", json={"total_amount": "100000"})
    assert converted.status_code == 201
    booking_id = converted.get_json()["id"]
    again = auth(admin, "POST", f"/api/enquiries/{enquiry_id}/convert", json={"total_amount": "100000"})
    assert again.status_code == 409

    booking = auth(admin, "PUT", f"/api/bookings/{booking_id}", json={
        "customer_id": str(customer_id),
        "service_id": "1",
        "event_name": "Mehta wedding",
        "event_date": "2026-12-18",
        "event_location": "Lake Pavilion",
        "city": "Udaipur",
        "total_amount": "100000",
        "status": "confirmed",
    })
    assert booking.status_code == 200
    missing = auth(admin, "DELETE", "/api/customers/9999")
    assert missing.status_code == 404


def test_payment_revenue_is_not_the_contract(admin):
    customer = auth(admin, "POST", "/api/customers", json={
        "full_name": "Neel Kapoor", "email": "neel@example.demo", "phone": "9833333333",
        "city": "Delhi", "registration_date": "2026-02-01",
    }).get_json()
    booking = auth(admin, "POST", "/api/bookings", json={
        "customer_id": str(customer["id"]),
        "service_id": "1",
        "event_name": "Kapoor wedding",
        "event_date": "2026-11-20",
        "event_location": "Civic Hall",
        "city": "Delhi",
        "total_amount": "100000",
        "status": "confirmed",
    })
    booking_id = booking.get_json()["id"]
    paid = auth(admin, "POST", "/api/payments", json={
        "booking_id": str(booking_id), "amount": "30000", "payment_date": "2026-03-01",
        "method": "upi", "status": "paid", "transaction_ref": "ADV1",
    })
    assert paid.status_code == 201
    pending = auth(admin, "POST", "/api/payments", json={
        "booking_id": str(booking_id), "amount": "70000", "payment_date": "2026-03-02",
        "method": "upi", "status": "pending",
    })
    assert pending.status_code == 201
    refund = auth(admin, "POST", "/api/payments", json={
        "booking_id": str(booking_id), "amount": "5000", "payment_date": "2026-03-05",
        "method": "bank_transfer", "status": "refunded",
    })
    assert refund.status_code == 201
    too_much = auth(admin, "POST", "/api/payments", json={
        "booking_id": str(booking_id), "amount": "90000", "payment_date": "2026-03-06",
        "method": "cash", "status": "paid",
    })
    assert too_much.status_code == 409
    detail = admin.get(f"/admin/bookings/{booking_id}")
    assert b"30,000" in detail.data or b"25,000" in detail.data
    summary = auth(admin, "GET", "/api/payments").get_json()["summary"]
    assert summary["net_revenue"] == 25000
    assert summary["net_revenue"] != 100000


def test_service_project_and_employee_limits(admin, employee):
    service = auth(admin, "POST", "/api/services", json={
        "name": "Engagement Photography", "category": "engagement",
        "description": "A short ceremony.", "base_price": "20000", "status": "active", "sort_order": "2",
    })
    assert service.status_code == 201
    toggled = auth(admin, "POST", f"/api/services/{service.get_json()['id']}/status", json={"status": "inactive"})
    assert toggled.status_code == 200
    blocked = auth(employee, "POST", "/api/services", json={
        "name": "Nope", "category": "x", "description": "x", "base_price": "10", "status": "active",
    })
    assert blocked.status_code == 403

    customer = auth(admin, "POST", "/api/customers", json={
        "full_name": "Sara Iyer", "email": "sara@example.demo", "phone": "9844444444",
        "city": "Goa", "registration_date": "2026-04-01",
    }).get_json()
    booking = auth(admin, "POST", "/api/bookings", json={
        "customer_id": str(customer["id"]), "service_id": "1", "event_name": "Iyer wedding",
        "event_date": "2026-08-01", "event_location": "Palm Lawns", "city": "Goa",
        "total_amount": "80000", "status": "confirmed",
        "team": [{"employee_id": "1", "team_role": "Lead Photographer", "is_lead": True}],
    }).get_json()
    project = auth(admin, "POST", "/api/projects", json={
        "booking_id": str(booking["id"]), "photographer_id": "1", "status": "not_started",
        "start_date": "2026-08-01", "delivery_date": "2026-08-20",
    })
    assert project.status_code == 201
    project_id = project.get_json()["id"]
    changed = auth(employee, "PUT", f"/api/projects/{project_id}", json={"status": "editing", "notes": "Selects are in"})
    assert changed.status_code == 200
    denied = auth(employee, "PUT", f"/api/projects/{project_id}", json={"status": "editing", "photographer_id": "1"})
    assert denied.status_code == 403


def test_analytics_and_reports(admin):
    empty = auth(admin, "GET", "/api/analytics?preset=custom&start=1990-01-01&end=1990-01-31")
    body = empty.get_json()
    assert empty.status_code == 200
    assert body["revenue"]["total_revenue"] == 0
    assert "Not enough data" in body["insights"][0]
    assert body["forecast"]["disclaimer"]
    assert body["enquiries"]["definition"].startswith("Conversion rate")

    customer = auth(admin, "POST", "/api/customers", json={
        "full_name": "Dev Shah", "email": "dev@example.demo", "phone": "9855555555",
        "city": "Pune", "registration_date": str(date.today()),
    }).get_json()
    booking = auth(admin, "POST", "/api/bookings", json={
        "customer_id": str(customer["id"]), "service_id": "1", "event_name": "Shah wedding",
        "event_date": str(date.today() + timedelta(days=30)), "event_location": "Garden Terrace",
        "city": "Pune", "total_amount": "50000", "status": "confirmed",
    }).get_json()
    auth(admin, "POST", "/api/payments", json={
        "booking_id": str(booking["id"]), "amount": "10000", "payment_date": str(date.today()),
        "method": "cash", "status": "paid",
    })
    live = auth(admin, "GET", "/api/dashboard?preset=this_year").get_json()
    revenue_card = next(item for item in live["kpis"] if item["key"] == "revenue")
    assert revenue_card["value"] == 10000

    report = auth(admin, "GET", "/api/reports/revenue?format=pdf&preset=this_year")
    assert report.status_code == 200
    assert report.data.startswith(b"%PDF")
    sheet = auth(admin, "GET", "/api/reports/customers?format=csv&preset=this_year")
    assert b"Customer Report" in sheet.data
    excel = auth(admin, "GET", "/api/reports/annual?format=xlsx&preset=this_year")
    assert excel.status_code == 200
    assert excel.data[:2] == b"PK"
