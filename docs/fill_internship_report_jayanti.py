"""Fill the university internship report template for Jayanti Jha / FotoInsight."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Inches, Pt

SRC = Path("/Users/madhavballabhkakkar/Downloads/AI_ML_Data_Science_Internship_Report_Template-2026.docx")
OUT = Path("/Users/madhavballabhkakkar/Downloads/FotoInsight_Internship_Report_Jayanti_Jha.docx")
ASSETS = Path(__file__).resolve().parent / "report_assets" / "compressed"

STUDENT_NAME = "Jayanti Jha"
STUDENT_ID = "K25341"
STUDENT_YEAR = "3rd Year"
DEMO_LINK = "https://fotoinsight.onrender.com/"
REPORT_PLACE = "Kota"
REPORT_DATE = "23 November 2026"
ORG_NAME = "Fotographiya Ventures Pvt. Ltd."
ORG_BRAND = "Fotographiya"
ROLE = "Data Analyst"
INTERNSHIP_START = "01 June 2026"
INTERNSHIP_END = "15 July 2026"
DURATION = "45 Days"
EXTERNAL_GUIDE = "Mohit Barthunia"
EXTERNAL_DESIGNATION = "Founder / CEO"
DIRECTOR = "Princu Kherada"
DIRECTOR_DESIGNATION = "Director"

SCREENSHOTS = [
    ("01_home.jpg", "Figure E.1 – Home page (public website)"),
    ("02_about.jpg", "Figure E.2 – About page"),
    ("03_services.jpg", "Figure E.3 – Services page"),
    ("04_portfolio.jpg", "Figure E.4 – Portfolio / gallery page"),
    ("05_contact.jpg", "Figure E.5 – Contact / enquiry form page"),
    ("06_login.jpg", "Figure E.6 – Studio (Admin) login page"),
    ("07_admin_dashboard.jpg", "Figure E.7 – Admin Overview dashboard"),
    ("11_enquiries.jpg", "Figure E.8 – Enquiries management screen"),
    ("08_analytics.jpg", "Figure E.9 – Analytics page (KPIs and definitions)"),
    ("09_analytics_charts.jpg", "Figure E.10 – Analytics charts (Chart.js)"),
    ("10_data_sync.jpg", "Figure E.11 – Data Sync (JSON / CSV / Excel + Firebase)"),
]


def set_para(paragraph, text: str) -> None:
    if paragraph.runs:
        paragraph.runs[0].text = text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(text)


def clear_and_add_picture(paragraph, image_path: Path, width_inches: float = 5.8) -> None:
    for run in paragraph.runs:
        run.text = ""
    if paragraph.runs:
        run = paragraph.runs[0]
    else:
        run = paragraph.add_run()
    run.add_picture(str(image_path), width=Inches(width_inches))
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER


def insert_caption_after(paragraph, caption: str):
    new_p = paragraph.insert_paragraph_before("") if False else None  # placate linters
    _ = new_p
    # python-docx has no direct insert_after; add at document end then move — use parent insert
    parent = paragraph._element.getparent()
    idx = parent.index(paragraph._element)
    from docx.oxml import OxmlElement
    from docx.text.paragraph import Paragraph

    p_elm = OxmlElement("w:p")
    parent.insert(idx + 1, p_elm)
    cap = Paragraph(p_elm, paragraph._parent)
    run = cap.add_run(caption)
    run.italic = True
    run.font.size = Pt(10)
    cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    return cap


def add_screenshot_block(doc: Document, after_paragraph, items: list[tuple[str, str]]) -> None:
    """Replace guideline text under Screenshots and append labelled images after that para."""
    set_para(
        after_paragraph,
        "The following screenshots were taken from the live deployment "
        f"({DEMO_LINK}). They show the public website and the admin analytics workflow.",
    )
    parent = after_paragraph._element.getparent()
    insert_at = parent.index(after_paragraph._element) + 1

    from docx.oxml import OxmlElement
    from docx.text.paragraph import Paragraph

    for filename, caption in reversed(items):
        # insert in reverse so final order is correct
        path = ASSETS / filename
        if not path.exists():
            continue
        # caption paragraph
        cap_elm = OxmlElement("w:p")
        parent.insert(insert_at, cap_elm)
        cap = Paragraph(cap_elm, after_paragraph._parent)
        run = cap.add_run(caption)
        run.italic = True
        run.font.size = Pt(10)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

        # image paragraph
        img_elm = OxmlElement("w:p")
        parent.insert(insert_at, img_elm)
        img_p = Paragraph(img_elm, after_paragraph._parent)
        img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_p.add_run().add_picture(str(path), width=Inches(5.7))


def main() -> None:
    doc = Document(str(SRC))

    exact = {
        "Course Name (Course Code)": (
            f"Bachelor of Computer Application (BCA) – {STUDENT_YEAR} – Internship / Project Work"
        ),
        "Month, YYYY": "November, 2026",
        "Paste Certificate Here": "Internship Completion Certificate – Fotographiya Ventures Pvt. Ltd.",
        "<Mention details – max 15 lines>": (
            "I sincerely thank Fotographiya Ventures Pvt. Ltd. for providing me the opportunity to complete a "
            f"{DURATION} internship as a {ROLE}. I am grateful to {EXTERNAL_GUIDE} ({EXTERNAL_DESIGNATION}) and "
            f"{DIRECTOR} ({DIRECTOR_DESIGNATION}) for their guidance and encouragement. I also thank the School of "
            "Computer Application and Technology, Career Point University, Kota, and my internal project guide for "
            "academic support. During this internship I worked on FotoInsight — a photography-studio website and "
            "business analytics system — and learned how enquiry-to-payment data can be turned into clear graphs and "
            "KPIs using Python, Pandas, and NumPy. Finally, I thank my family and friends for their support."
        ),
        "<Student Name>": STUDENT_NAME,
        "Place:                                                                                              ": (
            f"Place: {REPORT_PLACE}                                                                                              "
        ),
        "Date:": f"Date: {REPORT_DATE}",
        "Online Deployment / Live Demo Link: _______________________________________________________": (
            f"Online Deployment / Live Demo Link: {DEMO_LINK}"
        ),
        "Home Page:": f"Home Page: {DEMO_LINK} (screenshot attached in Annexure E)",
        "A: Data Flow Diagram (DFD)": "A: Data Flow Diagram (DFD) – FotoInsight enquiry-to-analytics flow",
        "B: Entity Relationship Diagram (ERD)": "B: Entity Relationship Diagram (ERD) – FotoInsight SQLite schema",
        "C: Use Case Diagram (UCD)": "C: Use Case Diagram (UCD) – Visitor, Admin, Employee",
        "D: Data Dictionary (DD)": "D: Data Dictionary (DD) – Key tables/fields",
        "E: Screen Shots": "E: Screen Shots – Public site, Admin, Analytics, Data Sync",
    }

    by_heading = {
        "Introduction": (
            "This report presents FotoInsight, a photography-studio website and office analytics system developed "
            f"during a {DURATION} internship as a {ROLE} at {ORG_NAME}. The system combines a public website for "
            "clients with a secure admin/staff panel for managing customers, enquiries, bookings, payments, and "
            "projects. The analytics module uses Pandas and NumPy to calculate revenue, conversion, customer "
            "segments, seasonal demand, and service performance, and presents results through interactive charts. "
            "The work demonstrates an end-to-end data path from operational records to business insights suitable "
            "for academic evaluation and viva demonstration."
        ),
        "Background": (
            "The photography and event industry depends on timely follow-up of enquiries, clear booking schedules, "
            "accurate collection of advances and balances, and understanding of which services and seasons generate "
            "revenue. Many small studios still track these activities in scattered notes or spreadsheets, which makes "
            "conversion analysis and cash-based revenue reporting difficult. A data-science-oriented web system is "
            "relevant because it stores structured transactional data and then applies analytical rules (revenue from "
            "collected payments, conversion of worked enquiries, seasonal demand) to support decisions. FotoInsight "
            "addresses this domain with Flask, SQLite, Pandas/NumPy analytics, Chart.js visualizations, local "
            "JSON/CSV/Excel persistence, and optional Firebase Realtime Database REST synchronization."
        ),
        "Problem Statement": (
            "Problem: Studio owners need one system that (a) captures public enquiries, (b) manages bookings and "
            "payments without treating unpaid contracts as cash, and (c) explains business performance with transparent "
            "formulas. Why analytics is needed: Without consistent definitions for revenue and conversion, reports "
            "become misleading. Proposed solution: FotoInsight implements an office workflow in Flask with SQLite, "
            "computes analytics in Pandas/NumPy (revenue = paid/partially paid − refunds; conversion = converted ÷ "
            "eligible statuses), visualizes results with Chart.js, exports snapshots to JSON/CSV/Excel, and can sync "
            "to Firebase via REST. A supervised linear forecast (scikit-learn) is shown only when history and fit "
            "quality are sufficient."
        ),
        "Objectives of the Internship / Study": (
            "1. To design and implement a photography-studio web application with public and admin modules.\n"
            "2. To model business data (customers, enquiries, bookings, payments, projects) and enforce clear money rules.\n"
            "3. To build a Pandas/NumPy analytics layer for revenue, conversion, customers, services, seasons, and locations.\n"
            "4. To provide Chart.js dashboards, report downloads (PDF/Excel/CSV), and local JSON/CSV/Excel persistence.\n"
            "5. To deploy the application online (Render + Gunicorn) and document the system for academic evaluation."
        ),
        "Scope of the Work": (
            "In-Scope: Public pages (Home, About, Services, Portfolio, Enquiry, Contact); Admin/Staff login; CRUD for "
            "customers, enquiries, bookings, payments, projects, and services; Analytics and Reports; Data Sync "
            "(JSON/CSV/Excel + Firebase REST); synthetic demo dataset for evaluation; live deployment on Render.\n"
            "Out of Scope: Real payment gateway integration; production-grade multi-tenant SaaS; native mobile apps; "
            "claiming demo figures as a real studio’s audited accounts; advanced deep-learning computer vision on photos."
        ),
        "Internship / Organization Overview": (
            f"This {DURATION} internship was completed at {ORG_NAME} ({ORG_BRAND}) as a {ROLE}, from "
            f"{INTERNSHIP_START} to {INTERNSHIP_END}. The academic internship/project work is submitted under the "
            "School of Computer Application and Technology (SOCAT), Career Point University, Kota, as partial "
            "fulfilment of the BCA programme. The practical focus was building a complete data-analytics-enabled "
            "web product for the photography-business domain."
        ),
        "About the Organization": (
            f"{ORG_NAME} ({ORG_BRAND}) is a photography and creative ventures organisation. During the internship, "
            f"work was carried out under the guidance of {EXTERNAL_GUIDE} ({EXTERNAL_DESIGNATION}) and "
            f"{DIRECTOR} ({DIRECTOR_DESIGNATION}). The organisation provided exposure to studio workflows and "
            "data-analysis practice relevant to enquiry handling, bookings, and business reporting. The academic "
            "project deliverable developed during this period is FotoInsight — a demonstration studio website with "
            "an analytics office panel."
        ),
        "Duration and Mode of the Internship": (
            f"Duration: {INTERNSHIP_START} to {INTERNSHIP_END} ({DURATION}).\n"
            "Mode: Hybrid / Remote development with cloud deployment on Render.\n"
            "Collaboration: GitHub repository and live hosted demo for guide/HOD review.\n"
            f"Role: {ROLE}."
        ),
        "Role and Responsibilities During the Internship": (
            f"Role: {ROLE} (BCA {STUDENT_YEAR} Intern) at {ORG_NAME}.\n"
            "Responsibilities: understanding studio enquiry-to-payment workflows; contributing to requirement "
            "analysis; working with structured data for analytics; supporting Flask-based modules; building "
            "Pandas/NumPy metrics (revenue, conversion, seasonal demand); preparing Chart.js dashboards; validating "
            "payment and conversion rules; documenting results; and assisting with deployment for demonstration."
        ),
        "Project Description": (
            "FotoInsight has two faces: a public marketing and enquiry website, and a private office for staff. "
            "Operational data is stored in SQLite. Analytics modules load records into Pandas DataFrames, compute KPIs "
            "with NumPy, return JSON to the browser, and render charts with Chart.js. Reports export PDF/Excel/CSV. "
            "The Data Sync module writes local JSON/CSV/Excel files and can push/pull a bundle through Firebase REST APIs."
        ),
        "Project Modules": (
            "1. Public Website Module – services catalogue, portfolio, enquiry and contact forms.\n"
            "2. Authentication & Authorization – admin and employee roles, hashed passwords, session security.\n"
            "3. Operations Module – customers, enquiries (assign/notes/convert), bookings (table/calendar), payments, projects.\n"
            "4. Analytics Module – revenue, customers, enquiry conversion, services, seasonal demand, locations, insights, forecast.\n"
            "5. Reports Module – PDF, Excel, and CSV downloads with date-range filters.\n"
            "6. Data Sync Module – local persistence (JSON/CSV/Excel) and Firebase Realtime Database REST synchronization.\n"
            "7. Deployment Module – Gunicorn production server hosted on Render."
        ),
        "Context Diagram (High Level)": (
            "External entities: Public Visitor, Admin, Employee, Firebase (optional cloud sync).\n"
            "Central process: FotoInsight System.\n"
            "Inputs: enquiry/contact forms, admin CRUD actions, date-range filters, sync commands.\n"
            "Outputs: web pages, KPI cards/charts, PDF/Excel/CSV reports, local data files, Firebase cloud snapshot.\n"
            "[Insert Level-0 DFD drawing in Annexure A.]"
        ),
        "System Architecture / Data Flow Overview": (
            "Browser (HTML/Jinja/Bootstrap/Chart.js) → Flask routes (validation, auth) → Models / SQLite → "
            "Analytics (Pandas + NumPy [+ scikit-learn for guarded forecast]) → JSON API → Chart.js UI.\n"
            "Parallel paths: Reports (fpdf2/openpyxl); Local store (JSON/CSV/Excel); Firebase REST sync.\n"
            "Deployment: Gunicorn behind Render HTTPS.\n"
            "[Insert architecture diagram.]"
        ),
        "Internship Training Details and Learning Outcomes": (
            "Training covered Python and Flask web development, relational data modelling with SQLite, Pandas/NumPy for "
            "business metrics, Chart.js visualization, OpenPyXL/fpdf2 reporting, Git/GitHub workflow, and cloud deployment "
            "with Gunicorn on Render. Learning outcomes include writing transparent analytics definitions, separating "
            "contract value from collected cash, role-based access control, and defending results in a viva with reproducible "
            "demo data."
        ),
        "Week-wise Training Activities": (
            "The week-wise plan for the 45-day internship is summarized in the table below."
        ),
        "Implementation Methodology": (
            "Methodology followed an iterative build: schema and seed data first, then operational CRUD screens, then "
            "analytics formulas and charts, then reports and sync, then deployment and viva checklist testing "
            "(including empty date ranges and payment status rules)."
        ),
        "Model Development Approach": (
            "Primary analytics are rule-based and statistical (aggregations, rates, percentiles, seasonal labels), not a "
            "black-box deep network—this keeps every KPI explainable in viva. For forecasting, a scikit-learn LinearRegression "
            "model is fitted on monthly series when at least eight active months exist and R² ≥ 0.15; otherwise the UI hides "
            "predictions and states that a straight line does not describe the history. Customer high-value segmentation uses "
            "the 75th percentile of lifetime collected spend after at least four paying customers exist."
        ),
        "Testing and Validation Strategy": (
            "Functional tests cover login failures, CSRF-protected APIs, enquiry idempotency via submission tokens, "
            "one-time enquiry-to-booking conversion, payment revenue ≠ booking contract, role permissions, empty analytics "
            "ranges, and report file headers. Manual validation checks that Paid/Partially Paid add cash, Pending is excluded, "
            "Refunded subtracts, and conversion excludes status New. Live health check: /health returns database up on Render."
        ),
        "Software Platform": (
            "Programming Language: Python 3.12+\n"
            "Web Framework: Flask 3, Jinja2, Gunicorn\n"
            "IDE: Cursor / VS Code\n"
            "Libraries: Pandas, NumPy, scikit-learn, OpenPyXL, fpdf2, python-dotenv\n"
            "Frontend: HTML5, Bootstrap 5, Chart.js\n"
            "Database: SQLite\n"
            "Cloud sync: Firebase Realtime Database REST API\n"
            "Local persistence: JSON, CSV, Excel"
        ),
        "Hardware Platform": (
            "Development machine: Apple macOS (ARM), sufficient RAM/SSD for Python analytics workloads, stable internet "
            "for GitHub and Render deployment. No dedicated GPU required."
        ),
        "Code": (
            "Important entry points:\n"
            "- run.py / wsgi.py – application entry\n"
            "- app/analytics/*.py – Pandas/NumPy metrics\n"
            "- app/local_store.py – JSON/CSV/Excel export\n"
            "- app/firebase_sync.py – Firebase REST PUT/GET\n"
            "- database/seed_data.py – synthetic demo data\n"
            "Revenue rule (conceptual): signed_amount = +amount for paid/partially_paid, −amount for refunded, 0 for pending; "
            "total_revenue = sum(signed_amount).\n"
            "[Selected UI screenshots are in Annexure E.]"
        ),
        "Tools, if any": (
            "GitHub – source control (https://github.com/Madhavballabhkakkar/FotoInsight)\n"
            "Render – free web hosting\n"
            "Firebase Console – Realtime Database for cloud sync demo\n"
            "Browser DevTools – API/UI verification"
        ),
        "Results and Discussion": (
            "On the seeded demo database for a ‘This year’ style window, analytics show collected revenue computed only from "
            "payment statuses, enquiry conversion with New excluded from the denominator, Wedding Photography among the most "
            "requested services, and city-wise booking contribution. Month-to-month revenue growth compares complete months only. "
            "Empty custom ranges correctly return zeros and an insufficient-data message rather than invented charts. "
            "Forecast may be withheld when R² is too low—this is intentional and viva-defensible. "
            "Live screenshots of these results are attached in Annexure E."
        ),
        "Advantages of this Project": (
            "• Transparent, viva-ready formulas for revenue and conversion\n"
            "• End-to-end studio workflow in one system\n"
            "• Pandas/NumPy analytics with Chart.js visuals\n"
            "• Local JSON/CSV/Excel exports for offline evidence\n"
            "• Optional Firebase REST cloud sync\n"
            "• Free online deployment for demonstration\n"
            "• Role separation between admin and staff"
        ),
        "Limitations and Assumptions": (
            "Assumptions: Demo rows are synthetic (is_demo=1); seasonal peak months follow a labeled North-Indian wedding "
            "calendar rule for teaching; payment status fields are correctly maintained by users.\n"
            "Limitations: Free Render instances sleep when idle; SQLite on free hosting is re-seeded on rebuild and is not a "
            "durable multi-user production database; deep-learning image understanding is not implemented; Firebase requires "
            "configured project URL; Chart.js is used for visualization while meeting the charting objective."
        ),
        "Future Scope and Further Enhancement of the Project": (
            "Future enhancements may include a real payment gateway, persistent managed database, Plotly dashboards, "
            "Tailwind-based UI refresh, explainable AI summaries, SMS/email reminders for follow-ups, and richer ML models "
            "for demand forecasting once longer real histories are available."
        ),
        "Project Repository Location": (
            "GitHub Repository: https://github.com/Madhavballabhkakkar/FotoInsight\n"
            "Contains source code, schema, seed script, documentation, and deployment files. Share this location with the HOD."
        ),
        "Online Deployment Link": (
            f"Online Deployment / Live Demo Link: {DEMO_LINK}\n"
            "Admin login for demo: admin / Admin@123\n"
            "Staff login for demo: employee / Employee@123"
        ),
        "Definitions, Acronyms, and Abbreviations": (
            "Key terms used in this report are defined in the abbreviation table below."
        ),
        "Conclusion": (
            f"During the {DURATION} internship as a {ROLE} at {ORG_NAME}, FotoInsight was developed as a "
            "data-analytics-oriented project outcome: a working studio website and office system, transparent "
            "Pandas/NumPy analytics, visual charts, report exports, local JSON/CSV/Excel persistence, Firebase REST "
            "sync capability, and a live Render deployment. The project reinforces that reliable business insights "
            "depend as much on clear definitions and clean operational data as on algorithms."
        ),
        "References": (
            "1. Flask Documentation – https://flask.palletsprojects.com/\n"
            "2. Pandas Documentation – https://pandas.pydata.org/docs/\n"
            "3. NumPy Documentation – https://numpy.org/doc/\n"
            "4. scikit-learn Documentation – https://scikit-learn.org/stable/\n"
            "5. Chart.js Documentation – https://www.chartjs.org/docs/\n"
            "6. OpenPyXL Documentation – https://openpyxl.readthedocs.io/\n"
            "7. Firebase Realtime Database REST API – https://firebase.google.com/docs/database/rest/start\n"
            "8. Render Documentation – https://render.com/docs\n"
            "9. Gunicorn Documentation – https://docs.gunicorn.org/\n"
            "10. Project repository – https://github.com/Madhavballabhkakkar/FotoInsight\n"
            f"11. Live demo – {DEMO_LINK}\n"
            f"12. Internship Completion Certificate – {ORG_NAME} ({INTERNSHIP_START} to {INTERNSHIP_END})"
        ),
    }

    annex_guidelines = {
        "(Mandatory) — Show dataset input, preprocessing steps, your model/processing component and prediction output flow.": (
            "(Mandatory) Insert DFD showing: Public forms / Admin actions → FotoInsight (SQLite + Pandas/NumPy) → "
            "Charts, Reports, JSON/CSV/Excel, Firebase."
        ),
        "(Mandatory) — Show dataset entities/attributes and their relationships, or your logical data model/schema if no relational database is used.": (
            "(Mandatory) Insert ERD for employees, users, customers, services, packages, enquiries, bookings, payments, "
            "projects, feedback, settings. See docs/ARCHITECTURE.md in the repository."
        ),
        "(Optional) — Show how a user interacts with the prediction/ML system, if applicable.": (
            "(Optional) Insert UCD: Visitor submits enquiry; Admin manages records and opens Analytics/Data Sync; "
            "Employee updates assigned work; System computes KPIs and optional forecast."
        ),
        "(Mandatory) — List dataset fields/attributes and their data types, similar to the example tables below.": (
            "(Mandatory) FotoInsight data dictionary tables are filled below (Users and Customers examples). "
            "Extend similarly for enquiries, bookings, and payments."
        ),
    }

    for paragraph in doc.paragraphs:
        text = paragraph.text
        if text in exact:
            set_para(paragraph, exact[text])
        elif text in annex_guidelines:
            set_para(paragraph, annex_guidelines[text])
        elif text.startswith("We hereby declare that this Project Report titled"):
            set_para(
                paragraph,
                "We hereby declare that this Project Report titled “FotoInsight – Photography Studio Website "
                "and Business Data Analytics System” submitted by us and approved by our project guide, the School "
                "of Computer Application and Technology (SOCAT), Career Point University, Kota, is our original work "
                f"carried out during the internship at {ORG_NAME} ({INTERNSHIP_START} to {INTERNSHIP_END}). "
                "The data used for analytics demonstration is synthetic demo data created for academic purposes and "
                "does not represent any real studio’s accounts.",
            )

    paragraphs = doc.paragraphs
    for index, paragraph in enumerate(paragraphs):
        heading = paragraph.text.strip()
        if heading not in by_heading:
            continue
        content = by_heading[heading]
        cursor = index + 1
        while cursor < len(paragraphs) and not paragraphs[cursor].text.strip():
            cursor += 1
        if cursor >= len(paragraphs):
            continue
        if paragraphs[cursor].style.name.startswith("Heading"):
            continue
        target = paragraphs[cursor]
        current = target.text.strip()
        if (
            current.startswith("<")
            or "Guidelines:" in current
            or current.startswith("Programming Language")
            or current.startswith("IDE / Notebook")
            or current.startswith("Libraries / Frameworks")
            or current.startswith("RAM, Processor")
            or current.startswith("Example:")
            or "______" in current
            or "e.g." in current
            or len(current) < 120
        ):
            set_para(target, content)
            if heading == "Software Platform":
                wipe = cursor + 1
                while wipe < len(paragraphs) and paragraphs[wipe].style.name.startswith("level"):
                    set_para(paragraphs[wipe], "")
                    wipe += 1

    # Certificate image under "Paste Certificate Here" replacement text
    for paragraph in doc.paragraphs:
        if paragraph.text.strip().startswith("Internship Completion Certificate"):
            # add image in next empty/following paragraph if possible
            clear_and_add_picture(paragraph, ASSETS / "jayanti_certificate.jpg", width_inches=5.5)
            insert_caption_after(
                paragraph,
                f"Certificate of Completion – {STUDENT_NAME}, {ROLE}, {ORG_NAME} "
                f"({INTERNSHIP_START} to {INTERNSHIP_END})",
            )
            break

    # Remove template dummy screenshot(s) that ship inside Annexure E
    from docx.oxml.ns import qn

    annex_e_started = False
    for paragraph in list(doc.paragraphs):
        text = paragraph.text.strip()
        if text.startswith("Annexure E") or text == "Screen Shots" or text.startswith("E: Screen"):
            annex_e_started = True
        if not annex_e_started:
            continue
        if text.startswith("Annexure ") and not text.startswith("Annexure E"):
            break
        drawings = paragraph._element.xpath('.//*[local-name()="drawing"]')
        if drawings and not text.startswith("Internship Completion"):
            # Drop empty template image paragraphs before we insert real screenshots
            paragraph._element.getparent().remove(paragraph._element)

    # Screenshots annexure
    for index, paragraph in enumerate(doc.paragraphs):
        t = paragraph.text.strip()
        if (
            t.startswith("<Guidelines: Show notebook/code execution screenshots")
            or t.startswith("Insert screenshots:")
            or "Show notebook/code execution screenshots" in t
        ):
            add_screenshot_block(doc, paragraph, SCREENSHOTS)
            break

    table0 = doc.tables[0]
    table0.rows[0].cells[0].text = (
        "GUIDE:\n"
        f"Project Guide Name (External): {EXTERNAL_GUIDE}\n"
        f"Designation: {EXTERNAL_DESIGNATION}, {ORG_NAME}\n"
        "Project Guide Name (Internal): [Fill Internal Guide Name]\n"
        "Designation: [Fill]"
    )
    table0.rows[0].cells[1].text = (
        "SUBMITTED BY:\n"
        f"{STUDENT_NAME}\n"
        f"Student ID: {STUDENT_ID}\n"
        f"Programme: BCA – {STUDENT_YEAR}"
    )

    table1 = doc.tables[1]
    table1.rows[0].cells[1].text = "FotoInsight – Photography Studio Website and Business Data Analytics System"
    table1.rows[0].cells[2].text = "FotoInsight – Photography Studio Website and Business Data Analytics System"
    table1.rows[1].cells[1].text = f"{STUDENT_NAME} ({STUDENT_ID})"
    table1.rows[1].cells[2].text = "Signature: _______________"
    table1.rows[3].cells[1].text = f"{EXTERNAL_GUIDE} ({EXTERNAL_DESIGNATION})"
    table1.rows[3].cells[2].text = "Signature: _______________"
    table1.rows[4].cells[1].text = "[Internal Guide Name]"
    table1.rows[4].cells[2].text = "Signature: _______________"

    weeks = [
        ("Week 1", "01–07 Jun 2026", "Organisation orientation, domain study, requirement analysis", "Understood studio workflow and analytics need"),
        ("Week 2", "08–14 Jun 2026", "Schema design, authentication, public website pages", "Built public site and secure login roles"),
        ("Week 3", "15–21 Jun 2026", "Customers, enquiries, bookings, payments, projects modules", "Completed operational CRUD workflows"),
        ("Week 4", "22–28 Jun 2026", "Pandas/NumPy analytics, Chart.js dashboards, report exports", "Delivered explainable business KPIs"),
        ("Week 5", "29 Jun–05 Jul 2026", "JSON/CSV/Excel local persistence, Firebase REST sync, testing", "Met compulsory local + cloud sync requirements"),
        ("Week 6", "06–15 Jul 2026", "Render deployment, documentation, certificate & viva prep", "Published live demo and final report"),
    ]
    week_table = doc.tables[2]
    for row_index, row_data in enumerate(weeks, start=1):
        for col_index, value in enumerate(row_data):
            week_table.rows[row_index].cells[col_index].text = value

    artifacts = doc.tables[3]
    artifacts.rows[1].cells[2].text = "GitHub: https://github.com/Madhavballabhkakkar/FotoInsight"
    artifacts.rows[2].cells[2].text = "GitHub commits / project progress notes"
    artifacts.rows[3].cells[2].text = "This filled report (Downloads / submitted softcopy)"
    artifacts.rows[4].cells[2].text = "GitHub repository + local tests/ folder"
    artifacts.rows[5].cells[2].text = (
        f"Live demo {DEMO_LINK} + Fotographiya completion certificate"
    )

    abbreviations = [
        ("AI", "Artificial Intelligence"),
        ("ML", "Machine Learning"),
        ("EDA", "Exploratory Data Analysis"),
        ("API", "Application Programming Interface"),
        ("REST", "Representational State Transfer"),
        ("KPI", "Key Performance Indicator"),
        ("CRUD", "Create, Read, Update, Delete"),
        ("CSV", "Comma-Separated Values"),
        ("JSON", "JavaScript Object Notation"),
        ("ORM/SQL", "Structured Query Language used via application models"),
        ("UI", "User Interface"),
        ("HTTPS", "Hypertext Transfer Protocol Secure"),
    ]
    abbr_table = doc.tables[4]
    while len(abbr_table.rows) < len(abbreviations) + 1:
        abbr_table.add_row()
    for row_index, (abbr, desc) in enumerate(abbreviations, start=1):
        abbr_table.rows[row_index].cells[0].text = abbr
        abbr_table.rows[row_index].cells[1].text = desc

    users = [
        ("Fields", "Data type", "Description"),
        ("id", "Integer", "Primary key of user"),
        ("username", "Text", "Login username (admin/employee)"),
        ("email", "Text", "User email address"),
        ("password_hash", "Text", "Hashed password (not plain text)"),
        ("role", "Text", "admin or employee"),
        ("display_name", "Text", "Name shown in admin UI"),
    ]
    customers = [
        ("Fields", "Data type", "Description"),
        ("id", "Integer", "Primary key of customer"),
        ("full_name", "Text", "Customer name"),
        ("email", "Text", "Customer email"),
        ("phone", "Text", "Customer phone"),
        ("city", "Text", "Customer city"),
        ("registration_date", "Date/Text", "Date of registration"),
        ("is_demo", "Integer", "1 = synthetic demo row"),
    ]
    user_table = doc.tables[5]
    while len(user_table.rows) < len(users):
        user_table.add_row()
    for row_index, row_data in enumerate(users):
        for col_index, value in enumerate(row_data):
            user_table.rows[row_index].cells[col_index].text = value

    cust_table = doc.tables[6]
    while len(cust_table.rows) < len(customers):
        cust_table.add_row()
    for row_index, row_data in enumerate(customers):
        for col_index, value in enumerate(row_data):
            cust_table.rows[row_index].cells[col_index].text = value

    for paragraph in doc.paragraphs:
        if paragraph.text.strip() == "User Table (USR)":
            set_para(paragraph, "Users Table (users)")
        elif paragraph.text.strip() == "Supplier Table (SUPP)":
            set_para(paragraph, "Customers Table (customers)")

    # Brief About the Company section (footer-like heading in template)
    for index, paragraph in enumerate(doc.paragraphs):
        if paragraph.text.strip() == "Brief About the Company":
            cursor = index + 1
            while cursor < len(doc.paragraphs) and not doc.paragraphs[cursor].text.strip():
                cursor += 1
            if cursor < len(doc.paragraphs):
                nxt = doc.paragraphs[cursor]
                if nxt.text.strip() in {"(Max 2 Pages)", ""} or "Max 2" in nxt.text:
                    set_para(
                        nxt,
                        f"{ORG_NAME} operates under the brand {ORG_BRAND} in photography and creative services. "
                        f"The internship organisation guided {STUDENT_NAME} as a {ROLE} for {DURATION} "
                        f"({INTERNSHIP_START} to {INTERNSHIP_END}). Leadership: {EXTERNAL_GUIDE} "
                        f"({EXTERNAL_DESIGNATION}) and {DIRECTOR} ({DIRECTOR_DESIGNATION}). The internship "
                        "project deliverable is FotoInsight, a studio website plus analytics office used for "
                        "academic demonstration of enquiry-to-insight data flows.",
                    )
            break

    doc.save(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
