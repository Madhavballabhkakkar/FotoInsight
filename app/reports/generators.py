"""Turn analytics results into a file an administrator can download."""

import csv
import io
from datetime import datetime

from fpdf import FPDF
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill

from app.analytics.customer_analysis import analyse as analyse_customers
from app.analytics.enquiry_analysis import analyse as analyse_enquiries
from app.analytics.revenue import analyse as analyse_revenue
from app.analytics.service_analysis import analyse as analyse_services
from app.constants import REVENUE_DEFINITION
from app.db import query_all
from app.utils import clean_rows

REPORTS = {
    "revenue": "Monthly Revenue Report",
    "bookings": "Booking Report",
    "customers": "Customer Report",
    "enquiries": "Enquiry Conversion Report",
    "services": "Service Performance Report",
    "annual": "Annual Business Report",
}


def generate(kind, start, end, file_format):
    if kind not in REPORTS:
        raise KeyError(kind)
    document = _build(kind, start, end)
    stamp = datetime.now().strftime("%Y-%m-%d")
    filename = f"fotoinsight-{kind}-{start.isoformat()}-to-{end.isoformat()}-{stamp}.{_extension(file_format)}"
    if file_format == "pdf":
        payload = _pdf(document)
        mime = "application/pdf"
    elif file_format == "xlsx":
        payload = _xlsx(document)
        mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    elif file_format == "csv":
        payload = _csv(document)
        mime = "text/csv"
    else:
        raise KeyError(file_format)
    return payload, mime, filename


def _extension(file_format):
    return "xlsx" if file_format == "xlsx" else file_format


def _build(kind, start, end):
    title = REPORTS[kind]
    if kind == "annual":
        title = f"Annual Business Report {start.year}" if start.year == end.year else "Business Report"
    summary, tables, chart = _sections(kind, start, end)
    return {
        "title": title,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "summary": summary,
        "tables": tables,
        "chart": chart,
        "note": "DEMO DATA. Synthetic records for academic demonstration. Not a real studio's performance. " + REVENUE_DEFINITION,
    }


def _sections(kind, start, end):
    if kind == "revenue":
        revenue = analyse_revenue(start, end)
        summary = [
            ("Collected revenue (INR)", revenue["total_revenue"]),
            ("Gross receipts before refunds", revenue["gross_collected"]),
            ("Refunds", revenue["refunds"]),
            ("Pending amounts excluded", revenue["pending_not_counted"]),
            ("Average contracted booking value", revenue["average_booking_value"] if revenue["average_booking_value"] is not None else "n/a"),
        ]
        tables = [
            _pairs_table("Revenue by month", revenue["monthly"]),
            _pairs_table("Revenue by service", revenue["by_service"]),
            _pairs_table("Revenue by city", revenue["by_location"]),
        ]
        return summary, tables, revenue["monthly"]
    if kind == "bookings":
        rows = clean_rows(query_all(
            """
            SELECT b.booking_code, c.full_name, b.event_name, b.event_type, b.event_date, b.city,
                   b.total_amount, b.status
            FROM bookings b JOIN customers c ON c.id = b.customer_id
            WHERE b.event_date >= %s AND b.event_date <= %s
            ORDER BY b.event_date
            """,
            (start, end),
        ))
        summary = [("Bookings in range", len(rows))]
        tables = [{
            "title": "Bookings",
            "columns": ["Code", "Customer", "Event", "Type", "Date", "City", "Contract", "Status"],
            "rows": [[row["booking_code"], row["full_name"], row["event_name"], row["event_type"], row["event_date"], row["city"], row["total_amount"], row["status"]] for row in rows],
        }]
        return summary, tables, None
    if kind == "customers":
        analysis = analyse_customers(start, end)
        summary = [
            ("Customers registered by period end", analysis["total_customers"]),
            ("New in range", analysis["new_customers"]),
            ("Returning with a booking in range", analysis["returning_customers"]),
            ("Average collected spend in range", analysis["average_spending"] if analysis["average_spending"] is not None else "n/a"),
        ]
        tables = [{
            "title": "Segments",
            "columns": ["Segment", "Rule", "Count"],
            "rows": [[item["name"], item["rule"], item["count"]] for item in analysis["segments"]],
        }, {
            "title": "High-value customers",
            "columns": ["Name", "City", "Collected spend", "Bookings"],
            "rows": [[item["name"], item["city"], item["spending"], item["bookings"]] for item in analysis["high_value"]],
        }]
        return summary, tables, analysis["growth"]
    if kind == "enquiries":
        analysis = analyse_enquiries(start, end)
        summary = [
            ("Total enquiries", analysis["total"]),
            ("Eligible (worked)", analysis["eligible"]),
            ("Converted", analysis["converted"]),
            ("Rejected", analysis["rejected"]),
            ("Still open", analysis["pending"]),
            ("New, excluded from the rate", analysis["new_excluded"]),
            ("Conversion rate %", analysis["conversion_rate"] if analysis["conversion_rate"] is not None else "n/a"),
            ("Average days to convert", analysis["average_conversion_days"] if analysis["average_conversion_days"] is not None else "n/a"),
        ]
        tables = [{
            "title": "By service",
            "columns": ["Service", "Enquiries", "Eligible", "Converted", "Rate %"],
            "rows": [[row["service"], row["total"], row["eligible"], row["converted"], row["conversion_rate"] if row["conversion_rate"] is not None else "n/a"] for row in analysis["by_service"]],
        }]
        chart = {"labels": analysis["monthly_rate"]["labels"], "values": [0 if value is None else value for value in analysis["monthly_rate"]["values"]]}
        return summary, tables, chart
    if kind == "services":
        analysis = analyse_services(start, end)
        summary = [
            ("Most enquiries", analysis["most_popular"] or "n/a"),
            ("Fewest enquiries", analysis["least_popular"] or "n/a"),
            ("Highest revenue", analysis["highest_revenue"] or "n/a"),
            ("Most bookings", analysis["most_booked"] or "n/a"),
        ]
        tables = [{
            "title": "Service performance",
            "columns": ["Service", "Enquiries", "Bookings", "Collected revenue", "Avg contract"],
            "rows": [[row["service"], row["enquiries"], row["bookings"], row["revenue"], row["average_booking_value"] if row["average_booking_value"] is not None else "n/a"] for row in analysis["rows"]],
        }]
        chart = {"labels": [row["service"] for row in analysis["rows"]], "values": [row["revenue"] for row in analysis["rows"]]}
        return summary, tables, chart
    revenue = analyse_revenue(start, end)
    enquiries = analyse_enquiries(start, end)
    services = analyse_services(start, end)
    customers = analyse_customers(start, end)
    summary = [
        ("Collected revenue", revenue["total_revenue"]),
        ("Enquiries", enquiries["total"]),
        ("Conversion rate %", enquiries["conversion_rate"] if enquiries["conversion_rate"] is not None else "n/a"),
        ("New customers", customers["new_customers"]),
        ("Highest-revenue service", services["highest_revenue"] or "n/a"),
    ]
    tables = [
        _pairs_table("Monthly collected revenue", revenue["monthly"]),
        _pairs_table("Quarterly collected revenue", revenue["quarterly"]),
        {
            "title": "Services",
            "columns": ["Service", "Enquiries", "Bookings", "Revenue"],
            "rows": [[row["service"], row["enquiries"], row["bookings"], row["revenue"]] for row in services["rows"]],
        },
    ]
    return summary, tables, revenue["monthly"]


def _pairs_table(title, series):
    return {
        "title": title,
        "columns": ["Period", "Value"],
        "rows": list(zip(series.get("labels", []), series.get("values", []))),
    }


def _pdf(document):
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=16)
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(0, 10, _safe(document["title"]), new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.cell(0, 6, _safe(f"Date range: {document['start']} to {document['end']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, _safe(f"Generated: {document['generated_at']}"), new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.set_font("Helvetica", "I", 8)
    pdf.multi_cell(0, 4, _safe(document["note"]))
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(0, 8, "Summary", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    for label, value in document["summary"]:
        pdf.cell(110, 6, _safe(label), new_x="RIGHT", new_y="TOP")
        pdf.cell(70, 6, _safe(value), new_x="LMARGIN", new_y="NEXT")
    if document["chart"] and document["chart"].get("values"):
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, "Chart", new_x="LMARGIN", new_y="NEXT")
        _bars(pdf, document["chart"]["labels"], document["chart"]["values"])
    for table in document["tables"]:
        if not table["rows"]:
            continue
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 12)
        pdf.cell(0, 8, _safe(table["title"]), new_x="LMARGIN", new_y="NEXT")
        _table(pdf, table["columns"], table["rows"])
    return bytes(pdf.output())


def _bars(pdf, labels, values):
    numbers = []
    for value in values:
        try:
            numbers.append(float(value))
        except (TypeError, ValueError):
            numbers.append(0.0)
    peak = max(numbers) if numbers else 0
    if peak <= 0:
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, "No positive values to chart.", new_x="LMARGIN", new_y="NEXT")
        return
    pdf.set_font("Helvetica", "", 8)
    for label, value in list(zip(labels, numbers))[:14]:
        pdf.cell(32, 6, _safe(label)[:16], new_x="RIGHT", new_y="TOP")
        x = pdf.get_x()
        y = pdf.get_y() + 1
        width = max(1, 110 * (value / peak))
        pdf.set_fill_color(166, 132, 86)
        pdf.rect(x, y, width, 4, "F")
        pdf.set_xy(x + 114, y - 1)
        pdf.cell(30, 6, _safe(f"{value:,.0f}"), new_x="LMARGIN", new_y="NEXT")


def _table(pdf, columns, rows):
    width = 190 / max(1, len(columns))
    pdf.set_font("Helvetica", "B", 8)
    for column in columns:
        pdf.cell(width, 6, _safe(column)[:22], border=1, new_x="RIGHT", new_y="TOP")
    pdf.ln(6)
    pdf.set_font("Helvetica", "", 8)
    for row in rows[:80]:
        if pdf.get_y() > 270:
            pdf.add_page()
        for cell in row:
            pdf.cell(width, 6, _safe(cell)[:28], border=1, new_x="RIGHT", new_y="TOP")
        pdf.ln(6)
    if len(rows) > 80:
        pdf.cell(0, 6, _safe(f"{len(rows) - 80} more rows are included in the Excel and CSV downloads."), new_x="LMARGIN", new_y="NEXT")


def _xlsx(document):
    book = Workbook()
    sheet = book.active
    sheet.title = "Summary"
    header = Font(bold=True, color="FFFFFF")
    fill = PatternFill("solid", fgColor="3E3428")
    sheet["A1"] = document["title"]
    sheet["A1"].font = Font(bold=True, size=14)
    sheet["A2"] = f"Date range: {document['start']} to {document['end']}"
    sheet["A3"] = f"Generated: {document['generated_at']}"
    sheet["A4"] = document["note"]
    sheet["A6"] = "Metric"
    sheet["B6"] = "Value"
    sheet["A6"].font = header
    sheet["B6"].font = header
    sheet["A6"].fill = fill
    sheet["B6"].fill = fill
    for index, (label, value) in enumerate(document["summary"], start=7):
        sheet.cell(index, 1, label)
        sheet.cell(index, 2, _excel_value(value))
    for table in document["tables"]:
        tab = book.create_sheet(_sheet_name(table["title"]))
        for col, name in enumerate(table["columns"], start=1):
            cell = tab.cell(1, col, name)
            cell.font = header
            cell.fill = fill
        for row_index, row in enumerate(table["rows"], start=2):
            for col, value in enumerate(row, start=1):
                tab.cell(row_index, col, _excel_value(value))
    buffer = io.BytesIO()
    book.save(buffer)
    return buffer.getvalue()


def _csv(document):
    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([document["title"]])
    writer.writerow(["Date range", document["start"], document["end"]])
    writer.writerow(["Generated", document["generated_at"]])
    writer.writerow(["Note", document["note"]])
    writer.writerow([])
    writer.writerow(["Metric", "Value"])
    for label, value in document["summary"]:
        writer.writerow([label, value])
    for table in document["tables"]:
        writer.writerow([])
        writer.writerow([table["title"]])
        writer.writerow(table["columns"])
        for row in table["rows"]:
            writer.writerow(row)
    return buffer.getvalue().encode("utf-8-sig")


def _sheet_name(title):
    cleaned = "".join(ch if ch.isalnum() or ch == " " else " " for ch in title)[:31]
    return cleaned or "Data"


def _excel_value(value):
    if isinstance(value, (int, float)):
        return value
    return _safe(value)


def _safe(value):
    text = "n/a" if value is None else str(value)
    return text.encode("latin-1", "replace").decode("latin-1")
