"""Numbers for the first admin screen. Charts use the same calculations as the analytics page."""

from app.analytics.customer_analysis import analyse as analyse_customers
from app.analytics.enquiry_analysis import analyse as analyse_enquiries
from app.analytics.insights import build as build_insights
from app.analytics.location import analyse as analyse_locations
from app.analytics.revenue import analyse as analyse_revenue
from app.analytics.seasonal import analyse as analyse_seasonal
from app.analytics.seasonal import created_by_month
from app.analytics.service_analysis import analyse as analyse_services
from app.db import query_one


def build(start, end, employee_id=None):
    if employee_id:
        return _employee(start, end, employee_id)
    revenue = analyse_revenue(start, end)
    enquiries = analyse_enquiries(start, end)
    customers = analyse_customers(start, end)
    services = analyse_services(start, end)
    seasonal = analyse_seasonal(start, end)
    locations = analyse_locations(start, end)
    upcoming = query_one(
        """
        SELECT COUNT(*) AS n FROM bookings
        WHERE event_date >= CURDATE()
          AND status IN ('confirmed', 'in_progress', 'on_hold')
        """
    )["n"]
    completed = query_one(
        """
        SELECT COUNT(*) AS n FROM projects
        WHERE status IN ('completed', 'delivered')
          AND delivery_date >= %s AND delivery_date <= %s
        """,
        (start, end),
    )["n"]
    confirmed = query_one(
        """
        SELECT COUNT(*) AS n FROM bookings
        WHERE DATE(created_at) >= %s AND DATE(created_at) <= %s
          AND status IN ('confirmed', 'in_progress', 'completed')
        """,
        (start, end),
    )["n"]
    pending_live = query_one(
        "SELECT COUNT(*) AS n FROM enquiries WHERE status IN ('new','contacted','follow_up','negotiation')"
    )["n"]
    distribution = {
        "labels": [row["service"] for row in services["rows"] if row["bookings"] > 0],
        "values": [row["bookings"] for row in services["rows"] if row["bookings"] > 0],
    }
    return {
        "scope": "admin",
        "kpis": [
            {"key": "customers", "label": "Total customers", "value": customers["total_customers"], "hint": "Registered on or before the end of the selected dates"},
            {"key": "enquiries", "label": "Total enquiries", "value": enquiries["total"], "hint": "Created during the selected dates"},
            {"key": "bookings", "label": "Confirmed bookings", "value": int(confirmed), "hint": "Confirmed, in progress, or completed. Cancelled and on hold are excluded."},
            {"key": "revenue", "label": "Total revenue", "value": revenue["total_revenue"], "money": True, "hint": "Collected payments only. Advances are not grossed up to the full booking."},
            {"key": "pending", "label": "Pending enquiries", "value": int(pending_live), "hint": "Live pipeline today: New, Contacted, Follow-up, Negotiation"},
            {"key": "upcoming", "label": "Upcoming events", "value": int(upcoming), "hint": "Live schedule from today. Not limited by the date filter."},
            {"key": "projects", "label": "Completed projects", "value": int(completed), "hint": "Delivery date inside the selected dates"},
            {"key": "conversion", "label": "Conversion rate", "value": enquiries["conversion_rate"], "percent": True, "hint": enquiries["definition"]},
        ],
        "charts": {
            "monthly_revenue": revenue["monthly"],
            "monthly_bookings": created_by_month(start, end),
            "service_distribution": distribution,
            "enquiry_status": enquiries["by_status"],
            "revenue_by_service": revenue["by_service"],
            "customer_growth": customers["growth"],
        },
        "highlights": build_insights(start, end, revenue, customers, enquiries, services, seasonal, locations)[:3],
    }


def _employee(start, end, employee_id):
    assigned_open = query_one(
        """
        SELECT COUNT(*) AS n FROM enquiries
        WHERE assigned_employee_id=%s AND status IN ('new','contacted','follow_up','negotiation')
        """,
        (employee_id,),
    )["n"]
    assigned_bookings = query_one(
        """
        SELECT COUNT(*) AS n
        FROM bookings b
        JOIN booking_team bt ON bt.booking_id = b.id
        WHERE bt.employee_id=%s AND DATE(b.created_at) >= %s AND DATE(b.created_at) <= %s
        """,
        (employee_id, start, end),
    )["n"]
    upcoming = query_one(
        """
        SELECT COUNT(*) AS n
        FROM bookings b
        JOIN booking_team bt ON bt.booking_id = b.id
        WHERE bt.employee_id=%s AND b.event_date >= CURDATE()
          AND b.status IN ('confirmed','in_progress','on_hold')
        """,
        (employee_id,),
    )["n"]
    active_projects = query_one(
        """
        SELECT COUNT(*) AS n FROM projects
        WHERE (photographer_id=%s OR editor_id=%s)
          AND status NOT IN ('completed','delivered')
        """,
        (employee_id, employee_id),
    )["n"]
    delayed = query_one(
        """
        SELECT COUNT(*) AS n FROM projects
        WHERE (photographer_id=%s OR editor_id=%s)
          AND delivery_date < CURDATE()
          AND status NOT IN ('completed','delivered')
        """,
        (employee_id, employee_id),
    )["n"]
    from app.db import query_all
    import pandas as pd

    rows = query_all(
        """
        SELECT DATE_FORMAT(b.event_date, '%%Y-%%m') AS month, COUNT(*) AS n
        FROM bookings b
        JOIN booking_team bt ON bt.booking_id = b.id
        WHERE bt.employee_id=%s AND b.event_date >= %s AND b.event_date <= %s AND b.status <> 'cancelled'
        GROUP BY month ORDER BY month
        """,
        (employee_id, start, end),
    )
    frame = pd.DataFrame(rows) if rows else pd.DataFrame(columns=["month", "n"])
    monthly = {
        "labels": [] if frame.empty else frame["month"].tolist(),
        "values": [] if frame.empty else [int(value) for value in frame["n"].tolist()],
    }
    status_rows = query_all(
        """
        SELECT status, COUNT(*) AS n FROM projects
        WHERE photographer_id=%s OR editor_id=%s
        GROUP BY status
        """,
        (employee_id, employee_id),
    )
    return {
        "scope": "employee",
        "kpis": [
            {"key": "enquiries", "label": "Assigned open enquiries", "value": int(assigned_open), "hint": "Live work assigned to you"},
            {"key": "bookings", "label": "Assigned bookings", "value": int(assigned_bookings), "hint": "Bookings recorded in the selected dates where you are on the team"},
            {"key": "upcoming", "label": "Upcoming events", "value": int(upcoming), "hint": "Your live schedule from today"},
            {"key": "projects", "label": "Open projects", "value": int(active_projects), "hint": "Projects where you are photographer or editor"},
            {"key": "delayed", "label": "Delayed projects", "value": int(delayed), "hint": "Delivery date has passed and the project is not finished"},
        ],
        "charts": {
            "monthly_bookings": monthly,
            "project_status": {
                "labels": [row["status"] for row in status_rows],
                "values": [int(row["n"]) for row in status_rows],
            },
        },
        "highlights": ["Revenue, payments, and studio-wide analytics are visible to administrators."],
    }
