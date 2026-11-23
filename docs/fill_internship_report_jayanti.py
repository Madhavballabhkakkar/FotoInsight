"""Fill internship report for Jayanti Jha — structure inspired by Aman Sharma (K26059), content for FotoInsight."""

from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt
from docx.text.paragraph import Paragraph

SRC = Path("/Users/madhavballabhkakkar/Downloads/AI_ML_Data_Science_Internship_Report_Template-2026.docx")
OUT = Path("/Users/madhavballabhkakkar/Downloads/FotoInsight_Internship_Report_Jayanti_Jha.docx")
ASSETS = Path(__file__).resolve().parent / "report_assets" / "compressed"

STUDENT_NAME = "Jayanti Jha"
STUDENT_ID = "K25341"
STUDENT_YEAR = "3rd Year"
COURSE = "Colloquium-II, (CAC771)"
REPORT_MONTH = "November 2026"
DEMO_LINK = "https://fotoinsight.onrender.com/"
REPORT_PLACE = "Kota, Rajasthan"
ORG_NAME = "Fotographiya Ventures Pvt. Ltd."
ORG_BRAND = "Fotographiya"
ORG_WEB = "https://www.fotographiya.com/"
ORG_ADDR = (
    "F-3, Ballabh Bari, Near 7 Wonders, Electricity Board Area, Kota, Rajasthan (Pincode: 324007)"
)
ORG_PHONE = "+91 9001110144"
ROLE = "Data Analyst"
INTERNSHIP_START = "01 June 2026"
INTERNSHIP_END = "15 July 2026"
DURATION = "45 Days"
CEO = "Mr. Mohit Barthunia"
CEO_ROLE = "Founder & CEO"
DIRECTOR = "Ms. Princu Kherada"
DIRECTOR_ROLE = "Director"
EXTERNAL_GUIDE = "Mr. Ajay Raj Kushwah"
INTERNAL_GUIDE = "Ms. Namrata Kashyap"
INTERNAL_DESIGNATION = "Assistant Professor"
HOD = "Dr. Garima Tyagi"
PROJECT_TITLE = "FotoInsight – Photography Studio Website and Business Data Analytics System"
GITHUB = "https://github.com/Madhavballabhkakkar/FotoInsight"

SCREENSHOTS = [
    ("01_home.jpg", "Figure E.1 – Home page of FotoInsight (public website)"),
    ("02_about.jpg", "Figure E.2 – About page"),
    ("03_services.jpg", "Figure E.3 – Services catalogue page"),
    ("04_portfolio.jpg", "Figure E.4 – Portfolio / gallery page"),
    ("05_contact.jpg", "Figure E.5 – Contact form page"),
    ("06_login.jpg", "Figure E.6 – Studio Admin login"),
    ("07_admin_dashboard.jpg", "Figure E.7 – Admin Overview dashboard"),
    ("11_enquiries.jpg", "Figure E.8 – Enquiries management"),
    ("08_analytics.jpg", "Figure E.9 – Analytics page (definitions and KPIs)"),
    ("09_analytics_charts.jpg", "Figure E.10 – Analytics charts rendered with Chart.js"),
    ("10_data_sync.jpg", "Figure E.11 – Data Sync (JSON / CSV / Excel + Firebase REST)"),
]


def set_para(paragraph, text: str) -> None:
    if paragraph.runs:
        paragraph.runs[0].text = text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(text)


def clear_and_add_picture(paragraph, image_path: Path, width_inches: float = 5.5) -> None:
    for run in paragraph.runs:
        run.text = ""
    run = paragraph.runs[0] if paragraph.runs else paragraph.add_run()
    run.add_picture(str(image_path), width=Inches(width_inches))
    paragraph.alignment = WD_ALIGN_PARAGRAPH.CENTER


def insert_paragraph_after(paragraph, text: str = "", italic: bool = False) -> Paragraph:
    parent = paragraph._element.getparent()
    idx = parent.index(paragraph._element)
    p_elm = OxmlElement("w:p")
    parent.insert(idx + 1, p_elm)
    new_p = Paragraph(p_elm, paragraph._parent)
    if text:
        run = new_p.add_run(text)
        run.italic = italic
        if italic:
            run.font.size = Pt(10)
        new_p.alignment = WD_ALIGN_PARAGRAPH.CENTER if italic else WD_ALIGN_PARAGRAPH.LEFT
    return new_p


def add_screenshot_block(after_paragraph, items: list[tuple[str, str]]) -> None:
    set_para(
        after_paragraph,
        "The following screenshots were taken from the live FotoInsight deployment "
        f"({DEMO_LINK}). They show the public website pages and the admin analytics workflow "
        "built during the internship.",
    )
    parent = after_paragraph._element.getparent()
    insert_at = parent.index(after_paragraph._element) + 1
    for filename, caption in reversed(items):
        path = ASSETS / filename
        if not path.exists():
            continue
        cap_elm = OxmlElement("w:p")
        parent.insert(insert_at, cap_elm)
        cap = Paragraph(cap_elm, after_paragraph._parent)
        run = cap.add_run(caption)
        run.italic = True
        run.font.size = Pt(10)
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER

        img_elm = OxmlElement("w:p")
        parent.insert(insert_at, img_elm)
        img_p = Paragraph(img_elm, after_paragraph._parent)
        img_p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        img_p.add_run().add_picture(str(path), width=Inches(5.7))


def remove_template_annexure_e_images(doc: Document) -> None:
    annex_e_started = False
    for paragraph in list(doc.paragraphs):
        text = paragraph.text.strip()
        if text.startswith("Annexure E") or text == "Screen Shots" or text.startswith("E: Screen"):
            annex_e_started = True
        if not annex_e_started:
            continue
        if text.startswith("Annexure ") and not text.startswith("Annexure E"):
            break
        if text.startswith("Home Page"):
            # keep text; remove only image-only dummy paras
            pass
        drawings = paragraph._element.xpath('.//*[local-name()="drawing"]')
        if drawings and not text:
            paragraph._element.getparent().remove(paragraph._element)


def replace_under_heading(doc: Document, by_heading: dict[str, str]) -> None:
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
            or len(current) < 140
            or current.startswith("This section")
            or current.startswith("In this chapter")
        ):
            set_para(target, content)
            if heading == "Software Platform":
                wipe = cursor + 1
                while wipe < len(paragraphs) and paragraphs[wipe].style.name.startswith("level"):
                    set_para(paragraphs[wipe], "")
                    wipe += 1


def main() -> None:
    doc = Document(str(SRC))

    exact = {
        "Course Name (Course Code)": COURSE,
        "Month, YYYY": REPORT_MONTH,
        "Paste Certificate Here": "Internship Completion Certificate",
        "<Student Name>": STUDENT_NAME,
        "Place:                                                                                              ": (
            f"Place: {REPORT_PLACE}                                                                                              "
        ),
        "Date:": f"Date: {REPORT_MONTH}",
        "Online Deployment / Live Demo Link: _______________________________________________________": (
            f"Online Deployment / Live Demo Link: {DEMO_LINK}"
        ),
        "Home Page:": f"Home Page: {DEMO_LINK}",
        "A: Data Flow Diagram (DFD)": "A: Data Flow Diagram (DFD)",
        "B: Entity Relationship Diagram (ERD)": "B: Entity Relationship Diagram (ERD)",
        "C: Use Case Diagram (UCD)": "C: Use Case Diagram (UCD)",
        "D: Data Dictionary (DD)": "D: Data Dictionary (DD)",
        "E: Screen Shots": "E: Screen Shots",
        "Annexure A": "Annexure A",
        "Annexure B": "Annexure B",
        "Annexure C": "Annexure C",
        "Annexure D": "Annexure D",
        "Annexure E": "Annexure E",
    }

    # Multi-paragraph acknowledgement (Aman style)
    ack_paras = [
        (
            f"I am grateful to {CEO} ({CEO_ROLE}), {ORG_NAME}, for giving me the internship opportunity "
            f"as a {ROLE} from {INTERNSHIP_START} to {INTERNSHIP_END}. He trusted me with real studio-workflow "
            "work around data and reporting, and I tried to do my best in every task. I also thank "
            f"{DIRECTOR} ({DIRECTOR_ROLE}) for guiding me during training and providing genuine feedback."
        ),
        (
            f"External Guide {EXTERNAL_GUIDE} reviewed my analytics definitions, database design and web "
            "modules during the internship and guided me whenever I got stuck while building FotoInsight, "
            "so that I could find the solution by myself."
        ),
        (
            f"Internal Guide {INTERNAL_GUIDE} kept a regular check on my progress and helped me present this "
            "work in a proper report format. Thanks are also due to the faculty members and Head of Department, "
            "School of Computer Application & Technology, Career Point University, Kota. I also thank my family "
            "members and friends for their patience."
        ),
    ]

    by_heading = {
        "Introduction": (
            f"This section describes my internship journey as a {ROLE} at {ORG_NAME}, Kota, for "
            f"{DURATION} from {INTERNSHIP_START} to {INTERNSHIP_END}. In this project, I developed and deployed "
            f"{PROJECT_TITLE}. Background, Problem Statement, Objectives and Scope of Work of this project "
            "are discussed in this chapter."
        ),
        "Background": (
            f"This project relates to photography and event studio operations within the wedding and event "
            f"industry. {ORG_NAME}, based in Kota, Rajasthan ({ORG_WEB}), provides wedding photography, "
            "pre-wedding shoots, destination weddings, corporate events, birthday parties, and related coverage. "
            "For such a business, enquiries arrive every day, bookings must be scheduled carefully, advances and "
            "balances must be tracked honestly, and the studio needs clear answers on which services and months "
            "actually generate collected money.\n\n"
            "Many small studios still keep these records in chat notes or scattered spreadsheets. That makes it "
            "hard to calculate conversion, cash-based revenue, returning customers, or seasonal demand in one place. "
            "A data-analytics-oriented web system is relevant because it stores structured operational data and then "
            "applies transparent rules using Python, Pandas and NumPy, and shows the result as Chart.js graphs for "
            "viva-ready decisions.\n\n"
            "FotoInsight was therefore built as a public studio website plus a secure office panel. Day-to-day "
            "records live in SQLite. Analytics load those records into DataFrames, compute KPIs, return JSON to the "
            "browser, and draw charts. Local JSON/CSV/Excel export and optional Firebase REST sync support the "
            "compulsory persistence requirement. The live demo is hosted on Render with Gunicorn."
        ),
        "Problem Statement": (
            "A photography studio needs one system that can capture public enquiries, convert them into bookings, "
            "record payments correctly, and explain performance with formulas that a student can defend in viva. "
            "If unpaid booking contracts are treated as revenue, the dashboard becomes misleading. If every enquiry "
            "status is mixed into conversion, the conversion rate also becomes wrong.\n\n"
            "Solution: FotoInsight is a Flask-based studio website and analytics office. Public visitors submit "
            "enquiries and contact messages. Admin and employee roles manage customers, enquiries, bookings, payments "
            "and projects. Revenue is calculated only from payment statuses (Paid / Partially Paid add cash; Refunded "
            "subtracts; Pending is ignored). Conversion uses eligible worked statuses and excludes New. Seasonal demand "
            "uses event dates. Charts are drawn with Chart.js. Reports export PDF/Excel/CSV. Data Sync writes local "
            "JSON/CSV/Excel files and can push/pull through Firebase REST. A linear forecast is shown only when history "
            "and fit quality are enough; otherwise it stays hidden."
        ),
        "Objectives of the Internship / Study": (
            "My objectives within this internship were:\n"
            f"1. Designing and building a public studio website and admin office for {ORG_NAME} / demonstration "
            "workflow using Flask, Jinja and Bootstrap.\n"
            "2. Modelling business data (customers, enquiries, bookings, payments, projects, services) with clear "
            "money rules so collected cash is never confused with contract value.\n"
            "3. Implementing a Pandas/NumPy analytics layer for revenue, enquiry conversion, customer segments, "
            "service performance, seasonal demand and location insights, with Chart.js visualization.\n"
            "4. Providing report downloads (PDF/Excel/CSV), local JSON/CSV/Excel persistence, and optional Firebase "
            "Realtime Database REST synchronization.\n"
            "5. Deploying the application online (Render + Gunicorn), documenting the work for Colloquium-II "
            "(CAC771), and preparing a viva-ready demo with synthetic data."
        ),
        "Scope of the Work": (
            f"Within the {DURATION} project timeline ({INTERNSHIP_START} to {INTERNSHIP_END}), FotoInsight was "
            f"developed as a studio website and business analytics system. Live demo: {DEMO_LINK}\n\n"
            "User Types:\n"
            "• Public Visitor: Unauthenticated visitor using mobile or desktop browser. Can view home, about, "
            "services, portfolio and contact pages, and submit an enquiry or contact message.\n"
            "• Studio Admin: Authenticated administrator who manages the whole office — customers, enquiries, "
            "bookings, payments, projects, services, analytics, reports, data sync and settings.\n"
            "• Employee: Authenticated staff user with limited access to assigned operational records.\n\n"
            "In-Scope Functionalities:\n"
            "• Public website with services catalogue, portfolio gallery, enquiry and contact forms.\n"
            "• Secure login with admin/employee roles, session security and CSRF-protected actions.\n"
            "• Operations CRUD for customers, enquiries (notes/assign/convert), bookings, payments and projects.\n"
            "• Analytics module with explainable KPIs and Chart.js charts.\n"
            "• Reports (PDF/Excel/CSV) and Data Sync (JSON/CSV/Excel + Firebase REST).\n"
            "• Live deployment on Render for guide/HOD review.\n\n"
            "Out of Scope:\n"
            "• Real payment gateway / UPI settlement.\n"
            "• Multi-tenant SaaS for many unrelated studios.\n"
            "• Native mobile applications.\n"
            "• Claiming demo analytics numbers as Fotographiya’s audited business accounts.\n"
            "• Deep-learning computer vision on photographs."
        ),
        "Internship / Organization Overview": (
            f"In this chapter I have described the organisation where I had my internship of {DURATION} as a "
            f"{ROLE}. I have also described the tasks and responsibilities that I had to perform during my "
            "internship period."
        ),
        "About the Organization": (
            f"{ORG_NAME} ({ORG_WEB}) is a private limited startup providing photography and video services for "
            f"various events including weddings. It is located at {ORG_ADDR}. A brief description about the company "
            "is provided in the section ‘Brief About the Company’ at the beginning of this report. Hence, only key "
            "points are presented here.\n\n"
            "This company provides photography for weddings, pre-wedding sessions, destination weddings, corporates, "
            "birthday events and portfolio sessions. Website and media platforms are also maintained to make it easy "
            f"for customers to get their services. The company is managed by {CEO} ({CEO_ROLE}) and {DIRECTOR} "
            f"({DIRECTOR_ROLE}). My technical mentor during the internship was {EXTERNAL_GUIDE} (External Guide)."
        ),
        "Duration and Mode of the Internship": (
            f"The project was conducted for a duration of {DURATION} ({INTERNSHIP_START} to {INTERNSHIP_END}) "
            "following an iterative build approach: schema and seed data, operational screens, analytics and charts, "
            f"reports and sync, then deployment. This internship is a part of BCA {COURSE} of Career Point University, "
            f"Kota. I was regularly monitored by my External Guide {EXTERNAL_GUIDE} and Internal Guide "
            f"{INTERNAL_GUIDE}. After the main application was developed, it was deployed on Render (Gunicorn) so that "
            "the guide and HOD can review the live demo."
        ),
        "Role and Responsibilities During the Internship": (
            f"My designation was {ROLE} (Intern). I worked on FotoInsight from planning to deployment, and my main "
            "responsibilities and deliverables were:\n\n"
            "• Planning and data understanding: Studied studio enquiry-to-payment workflow. Finalised transparent "
            "definitions for revenue, conversion and seasonal demand. Planned public pages and admin modules.\n"
            "• Database and office modules: Helped design SQLite schema for customers, enquiries, bookings, payments, "
            "projects and services. Supported Flask routes, forms validation, role-based access and seed demo data.\n"
            "• Analytics and visualization: Built Pandas/NumPy calculations for KPIs, monthly trends, service "
            "performance and location insights. Connected JSON APIs to Chart.js charts on the Analytics page.\n"
            "• Reports, sync and deployment: Supported PDF/Excel/CSV report exports, local JSON/CSV/Excel persistence, "
            "Firebase REST sync screen, testing of empty date ranges and payment rules, documentation, and Render "
            "deployment for viva demonstration.\n\n"
            "At the end of the internship, I delivered the working application along with this report and the "
            "completion certificate."
        ),
        "Project Description": (
            "FotoInsight is the application I built and demonstrated during the internship. It has a public marketing "
            "and enquiry website, and a private office for staff. Breakdown of each module is given below, along with "
            "architecture overview, skills developed and the week-wise plan over the course of 45 days."
        ),
        "Project Modules": (
            "1. Public Website Module: Home, About, Services, Portfolio, Contact and Enquiry forms for visitors.\n"
            "2. Authentication and Authorization Module: Admin and employee login, hashed passwords, sessions and CSRF.\n"
            "3. Operations Module: Customers, enquiries (assign/notes/convert), bookings, payments and projects.\n"
            "4. Analytics Module: Revenue, customers, conversion, services, seasons, locations, insights and guarded forecast.\n"
            "5. Reports Module: PDF, Excel and CSV downloads with date-range filters.\n"
            "6. Data Sync Module: Local JSON/CSV/Excel files and Firebase Realtime Database REST push/pull.\n"
            "7. Deployment Module: Gunicorn production server hosted on Render."
        ),
        "Context Diagram (High Level)": (
            "External entities: Public Visitor, Admin, Employee, and Firebase (optional cloud sync).\n"
            "Central process: FotoInsight System.\n"
            "Inputs: enquiry/contact forms, admin CRUD actions, date-range filters, sync commands.\n"
            "Outputs: web pages, KPI cards/charts, PDF/Excel/CSV reports, local data files, Firebase snapshot.\n"
            "Please see Annexure A for the Data Flow Diagram drawing."
        ),
        "System Architecture / Data Flow Overview": (
            "Browser (HTML / Jinja / Bootstrap / Chart.js) → Flask routes (validation, auth) → Models / SQLite → "
            "Analytics (Pandas + NumPy [+ scikit-learn for guarded forecast]) → JSON API → Chart.js UI.\n"
            "Parallel paths: Reports (fpdf2 / OpenPyXL); Local store (JSON/CSV/Excel); Firebase REST sync.\n"
            "Deployment: Gunicorn behind Render HTTPS.\n"
            f"Live URL: {DEMO_LINK}"
        ),
        "Internship Training Details and Learning Outcomes": (
            "Training covered Python and Flask web development, relational modelling with SQLite, Pandas/NumPy for "
            "business metrics, Chart.js visualization, OpenPyXL/fpdf2 reporting, Git/GitHub workflow, and cloud "
            "deployment with Gunicorn on Render. Learning outcomes include writing transparent analytics definitions, "
            "separating contract value from collected cash, role-based access control, and defending results in a viva "
            "with reproducible demo data."
        ),
        "Week-wise Training Activities": (
            "The week-wise plan for the 45-day internship is summarized in the table below."
        ),
        "Implementation Methodology": (
            "Methodology followed an iterative build: schema and seed data first, then operational CRUD screens, then "
            "analytics formulas and charts, then reports and sync, then deployment and viva checklist testing "
            "(including empty date ranges and payment status rules). This kept every KPI explainable instead of hiding "
            "logic inside a black-box model."
        ),
        "Model Development Approach": (
            "Primary analytics are rule-based and statistical (aggregations, rates, percentiles, seasonal labels). "
            "This keeps every KPI explainable in viva. For forecasting, a scikit-learn LinearRegression model is fitted "
            "on monthly series when at least eight active months exist and R² ≥ 0.15; otherwise the UI hides predictions "
            "and states that a straight line does not describe the history. High-value customers use the 75th percentile "
            "of lifetime collected spend after enough paying customers exist."
        ),
        "Testing and Validation Strategy": (
            "Functional checks covered login failures, CSRF-protected APIs, enquiry submission tokens, one-time "
            "enquiry-to-booking conversion, payment revenue ≠ booking contract, role permissions, empty analytics "
            "ranges, and report file headers. Manual validation checked that Paid/Partially Paid add cash, Pending is "
            "excluded, Refunded subtracts, and conversion excludes status New. Live health check: /health on Render."
        ),
        "Software Platform": (
            "Programming Language: Python 3.12+\n"
            "Web Framework: Flask 3, Jinja2, Gunicorn\n"
            "IDE: Cursor / VS Code\n"
            "Libraries: Pandas, NumPy, scikit-learn, OpenPyXL, fpdf2, python-dotenv\n"
            "Frontend: HTML5, Bootstrap 5, Chart.js\n"
            "Database: SQLite\n"
            "Cloud sync: Firebase Realtime Database REST API\n"
            "Hosting: Render (HTTPS)\n"
            "Local persistence: JSON, CSV, Excel"
        ),
        "Hardware Platform": (
            "Development machine: Apple macOS (ARM), sufficient RAM/SSD for Python analytics workloads, stable internet "
            "for GitHub and Render deployment. No dedicated GPU required."
        ),
        "Code": (
            "Important entry points of FotoInsight:\n"
            "• run.py / wsgi.py – application entry\n"
            "• app/analytics/*.py – Pandas/NumPy metrics\n"
            "• app/local_store.py – JSON/CSV/Excel export\n"
            "• app/firebase_sync.py – Firebase REST PUT/GET\n"
            "• database/seed_data.py – synthetic demo data\n\n"
            "Revenue rule (conceptual): signed_amount = +amount for paid/partially_paid, −amount for refunded, "
            "0 for pending; total_revenue = sum(signed_amount).\n"
            "Selected UI screenshots are placed in Annexure E."
        ),
        "Tools, if any": (
            f"• GitHub – source control ({GITHUB})\n"
            "• Render – web hosting for live demo\n"
            "• Firebase Console – Realtime Database for cloud sync demo\n"
            "• Browser DevTools – API/UI verification"
        ),
        "Results and Discussion": (
            "On the seeded demo database for a ‘This year’ window, analytics show collected revenue computed only from "
            "payment statuses, enquiry conversion with New excluded from the denominator, Wedding Photography among the "
            "most requested services, and city-wise booking contribution. Month-to-month revenue growth compares complete "
            "months only. Empty custom ranges correctly return zeros and an insufficient-data message rather than invented "
            "charts. Forecast may be withheld when R² is too low — this is intentional and viva-defensible.\n\n"
            "Principal screens and features are shown in Annexure E (Home, Services, Portfolio, Login, Overview, "
            "Enquiries, Analytics and Data Sync). The live system confirms that the internship objectives — website, "
            "office workflow, explainable analytics, sync and deployment — were achieved for demonstration purposes."
        ),
        "Advantages of this Project": (
            "7.1 Usability: Public pages are simple for visitors; admin screens keep office work in one place.\n"
            "7.2 Transparency: Revenue and conversion formulas are written on the Analytics page and can be defended in viva.\n"
            "7.3 Efficiency: One system covers enquiry → booking → payment → insight instead of scattered sheets.\n"
            "7.4 Visualization: Chart.js graphs make monthly and service trends easy to explain.\n"
            "7.5 Persistence: Local JSON/CSV/Excel export and optional Firebase REST sync meet compulsory storage needs.\n"
            "7.6 Availability: Live Render demo link can be opened by guide/HOD without installing the project locally."
        ),
        "Limitations and Assumptions": (
            "8.1 Assumptions: Demo rows are synthetic (is_demo=1) for academic demonstration. Seasonal peak months follow "
            "a labelled North-Indian wedding calendar rule for teaching. Payment status fields are maintained correctly "
            "by users of the office panel.\n\n"
            "8.2 Limitations: Free Render instances may sleep when idle. SQLite on free hosting is re-seeded on rebuild "
            "and is not a durable multi-user production database. Deep-learning image understanding is not implemented. "
            "Firebase requires a configured project URL. Demo figures must not be read as Fotographiya’s real audited "
            "accounts."
        ),
        "Future Scope and Further Enhancement of the Project": (
            "Future enhancements may include a real payment gateway, a managed persistent database, richer dashboards, "
            "SMS/email reminders for enquiry follow-ups, and stronger forecasting once longer real studio histories "
            "are available."
        ),
        "Project Repository Location": (
            f"GitHub Repository: {GITHUB}\n"
            "Contains source code, schema, seed script, documentation and deployment files."
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
            f"During the {DURATION} internship as a {ROLE} at {ORG_NAME}, I developed and demonstrated FotoInsight — "
            "a photography studio website with an office analytics panel. The work covered public pages, secure admin "
            "workflows, transparent Pandas/NumPy KPIs, Chart.js graphs, report exports, local JSON/CSV/Excel persistence, "
            "Firebase REST sync capability, and a live Render deployment. The main learning is that reliable business "
            "insights depend on clear definitions and clean operational data as much as on algorithms. I am thankful to "
            f"{CEO}, {DIRECTOR}, {EXTERNAL_GUIDE} and {INTERNAL_GUIDE} for their guidance."
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
            f"10. Project repository – {GITHUB}\n"
            f"11. Live demo – {DEMO_LINK}\n"
            f"12. Company website – {ORG_WEB}\n"
            f"13. Internship Completion Certificate – {ORG_NAME} ({INTERNSHIP_START} to {INTERNSHIP_END})"
        ),
    }

    annex_guidelines = {
        "(Mandatory) — Show dataset input, preprocessing steps, your model/processing component and prediction output flow.": (
            "(Mandatory) DFD: Public forms / Admin actions → FotoInsight (SQLite + Pandas/NumPy) → Charts, Reports, "
            "JSON/CSV/Excel, Firebase."
        ),
        "(Mandatory) — Show dataset entities/attributes and their relationships, or your logical data model/schema if no relational database is used.": (
            "(Mandatory) ERD for users, customers, services, enquiries, bookings, payments, projects, feedback, settings. "
            "See docs/ARCHITECTURE.md in the repository."
        ),
        "(Optional) — Show how a user interacts with the prediction/ML system, if applicable.": (
            "(Optional) UCD: Visitor submits enquiry; Admin manages records and opens Analytics/Data Sync; Employee "
            "updates assigned work; System computes KPIs and optional forecast."
        ),
        "(Mandatory) — List dataset fields/attributes and their data types, similar to the example tables below.": (
            "(Mandatory) Data dictionary tables for Users and Customers are filled below. Extend similarly for "
            "enquiries, bookings and payments."
        ),
    }

    # Exact replacements
    for paragraph in doc.paragraphs:
        text = paragraph.text
        if text in exact:
            set_para(paragraph, exact[text])
        elif text in annex_guidelines:
            set_para(paragraph, annex_guidelines[text])
        elif text.startswith("We hereby declare that this Project Report titled"):
            set_para(
                paragraph,
                f"I hereby declare that this Project Report titled {PROJECT_TITLE}, submitted by me to the School "
                "of Computer Application and Technology (SOCAT), Career Point University, Kota, with the approval of "
                "my project guides, is a bona fide work undertaken by me. It has not been submitted to any other "
                "University or Institution for the award of any degree or diploma, and it has not been published before. "
                "The analytics demonstration data is synthetic demo data for academic purposes and does not represent "
                "any real studio’s audited accounts.",
            )

    # Acknowledgement block
    for index, paragraph in enumerate(doc.paragraphs):
        if paragraph.text.strip() == "ACKNOWLEDGEMENT":
            cursor = index + 1
            while cursor < len(doc.paragraphs) and not doc.paragraphs[cursor].text.strip():
                cursor += 1
            if cursor < len(doc.paragraphs):
                set_para(doc.paragraphs[cursor], ack_paras[0])
                # append remaining ack paragraphs after first
                anchor = doc.paragraphs[cursor]
                for extra in reversed(ack_paras[1:]):
                    insert_paragraph_after(anchor, extra, italic=False)
            break

    replace_under_heading(doc, by_heading)

    # Brief About the Company
    for index, paragraph in enumerate(doc.paragraphs):
        if paragraph.text.strip() == "Brief About the Company":
            cursor = index + 1
            while cursor < len(doc.paragraphs) and not doc.paragraphs[cursor].text.strip():
                cursor += 1
            if cursor < len(doc.paragraphs):
                nxt = doc.paragraphs[cursor]
                set_para(
                    nxt,
                    f"{ORG_NAME} is a wedding and events photography and videography company based in Kota, Rajasthan. "
                    f"The studio is located at {ORG_ADDR}. Contact number: {ORG_PHONE}. It is managed by {CEO} "
                    f"({CEO_ROLE}) and {DIRECTOR} ({DIRECTOR_ROLE}). Website: {ORG_WEB}.\n\n"
                    "Overview: Services include Wedding, Pre-Wedding, Destination Wedding, Corporate Events, Birthday "
                    "events and Portfolio Shoots. For a photography business, a clear website, enquiry capture, booking "
                    "and payment tracking, and honest analytics are required. During my 45-day internship under the "
                    f"{ROLE} role from {INTERNSHIP_START} to {INTERNSHIP_END}, I worked on FotoInsight for this need. "
                    f"My External Guide was {EXTERNAL_GUIDE}.",
                )
            break

    # Certificate image
    for paragraph in doc.paragraphs:
        if paragraph.text.strip() in {"Internship Completion Certificate", "Certificate"} or paragraph.text.strip().startswith(
            "Internship Completion Certificate"
        ):
            # Keep a short label then image in same area
            set_para(paragraph, "Internship Completion Certificate")
            img_p = insert_paragraph_after(paragraph, "")
            clear_and_add_picture(img_p, ASSETS / "jayanti_certificate.jpg", width_inches=5.5)
            insert_paragraph_after(
                img_p,
                f"Certificate of Completion – {STUDENT_NAME}, {ROLE}, {ORG_NAME} "
                f"({INTERNSHIP_START} to {INTERNSHIP_END})",
                italic=True,
            )
            break

    remove_template_annexure_e_images(doc)

    for paragraph in doc.paragraphs:
        t = paragraph.text.strip()
        if (
            t.startswith("<Guidelines: Show notebook/code execution screenshots")
            or "Show notebook/code execution screenshots" in t
            or t.startswith("Insert screenshots:")
        ):
            add_screenshot_block(paragraph, SCREENSHOTS)
            break

    # Cover tables
    table0 = doc.tables[0]
    table0.rows[0].cells[0].text = (
        "GUIDE:\n"
        f"{EXTERNAL_GUIDE} (External)\n"
        "Designation: Project Guide (External)\n"
        f"{INTERNAL_GUIDE} (Internal)\n"
        f"{INTERNAL_DESIGNATION}"
    )
    table0.rows[0].cells[1].text = (
        "SUBMITTED BY:\n"
        f"{STUDENT_NAME}\n"
        f"({STUDENT_ID})"
    )

    table1 = doc.tables[1]
    table1.rows[0].cells[1].text = PROJECT_TITLE
    table1.rows[0].cells[2].text = PROJECT_TITLE
    table1.rows[1].cells[1].text = f"{STUDENT_NAME} ({STUDENT_ID})"
    table1.rows[1].cells[2].text = "Signature: ___________________"
    table1.rows[3].cells[1].text = EXTERNAL_GUIDE
    table1.rows[3].cells[2].text = "Signature: ___________________"
    table1.rows[4].cells[1].text = INTERNAL_GUIDE
    table1.rows[4].cells[2].text = "Signature: ___________________"

    weeks = [
        (
            "Week 1",
            "01 June 2026 to 07 June 2026 (Days 1 to 7)",
            "Organisation orientation, studio workflow study, requirement analysis for enquiry-to-payment analytics",
            "Understood Fotographiya workflow and why transparent KPIs are needed",
        ),
        (
            "Week 2",
            "08 June 2026 to 14 June 2026 (Days 8 to 14)",
            "Schema design, authentication roles, public website pages (Home/About/Services/Portfolio/Contact)",
            "Built public site structure and secure login roles",
        ),
        (
            "Week 3",
            "15 June 2026 to 21 June 2026 (Days 15 to 21)",
            "Customers, enquiries, bookings, payments and projects modules with validation rules",
            "Completed operational CRUD workflows used as analytics source data",
        ),
        (
            "Week 4",
            "22 June 2026 to 28 June 2026 (Days 22 to 28)",
            "Pandas/NumPy analytics (revenue, conversion, seasons), Chart.js dashboards, report exports",
            "Delivered explainable business KPIs and graphs",
        ),
        (
            "Week 5",
            "29 June 2026 to 05 July 2026 (Days 29 to 35)",
            "JSON/CSV/Excel local persistence, Firebase REST sync screen, testing of payment and empty-range rules",
            "Met compulsory local + cloud sync requirements",
        ),
        (
            "Week 6",
            "06 July 2026 to 15 July 2026 (Days 36 to 45)",
            "Render deployment, documentation, certificate process and viva preparation",
            "Published live demo and prepared final Colloquium report",
        ),
    ]
    week_table = doc.tables[2]
    for row_index, row_data in enumerate(weeks, start=1):
        if row_index >= len(week_table.rows):
            break
        for col_index, value in enumerate(row_data):
            week_table.rows[row_index].cells[col_index].text = value

    artifacts = doc.tables[3]
    artifacts.rows[1].cells[2].text = f"GitHub: {GITHUB}"
    artifacts.rows[2].cells[2].text = "GitHub commits / progress notes"
    artifacts.rows[3].cells[2].text = "This filled report softcopy (Downloads)"
    artifacts.rows[4].cells[2].text = f"GitHub repository + live demo {DEMO_LINK}"
    artifacts.rows[5].cells[2].text = f"Internship Completion Certificate – {ORG_NAME}"
    for row in artifacts.rows[1:]:
        row.cells[3].text = f"{INTERNAL_GUIDE} / __________"
        row.cells[4].text = f"{HOD} / __________"

    abbreviations = [
        ("API", "Application Programming Interface"),
        ("BCA", "Bachelor of Computer Application"),
        ("CRUD", "Create, Read, Update, Delete"),
        ("CSV", "Comma-Separated Values"),
        ("DFD", "Data Flow Diagram"),
        ("ERD", "Entity Relationship Diagram"),
        ("HTTPS", "Hypertext Transfer Protocol Secure"),
        ("JSON", "JavaScript Object Notation"),
        ("KPI", "Key Performance Indicator"),
        ("ORM/SQL", "Structured Query Language used via application models"),
        ("REST", "Representational State Transfer"),
        ("UI", "User Interface"),
        ("UCD", "Use Case Diagram"),
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

    # Acknowledgement signature block: Name then Student ID (Aman style)
    seen_name = False
    for paragraph in doc.paragraphs:
        t = paragraph.text.strip()
        if t in {"<Student Name>", STUDENT_NAME}:
            if not seen_name:
                set_para(paragraph, STUDENT_NAME)
                seen_name = True
            else:
                set_para(paragraph, STUDENT_ID)
                break

    # Footer / header (Aman style)
    for sec in doc.sections:
        for p in sec.footer.paragraphs:
            if "<Project Name>" in p.text or p.text.startswith("Project Title:"):
                new = p.text.replace("<Project Name>", PROJECT_TITLE)
                if "Project Title:" in new and PROJECT_TITLE not in new:
                    # if placeholder already cleared oddly, force title
                    new = f"Project Title: {PROJECT_TITLE}"
                if p.runs:
                    p.runs[0].text = new
                    for r in p.runs[1:]:
                        r.text = ""
                else:
                    p.add_run(new)
        for p in sec.header.paragraphs:
            if "CA005A" in p.text or "Version 6.0" in p.text or p.text.startswith("CPU-SOCA"):
                if p.runs:
                    p.runs[0].text = "CPU-SOCA\t\tCAC771"
                    for r in p.runs[1:]:
                        r.text = ""

    # Drop leftover template dummy screenshot (large PNG) if still present
    dummy_rids = set()
    for rel_id, rel in list(doc.part.rels.items()):
        if (
            "image" in rel.reltype
            and rel.target_part.content_type == "image/png"
            and len(rel.target_part.blob) > 900000
        ):
            dummy_rids.add(rel_id)
    for paragraph in list(doc.paragraphs):
        blips = paragraph._element.xpath('.//*[local-name()="blip"]')
        rids = [b.get(qn("r:embed")) for b in blips]
        if any(r in dummy_rids for r in rids):
            paragraph._element.getparent().remove(paragraph._element)
    for rel_id in list(dummy_rids):
        try:
            doc.part.drop_rel(rel_id)
        except Exception:
            pass

    doc.save(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
