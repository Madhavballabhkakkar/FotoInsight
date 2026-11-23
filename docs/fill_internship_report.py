"""Fill the university internship report template for FotoInsight."""

from pathlib import Path

from docx import Document

SRC = Path("/Users/madhavballabhkakkar/Downloads/AI_ML_Data_Science_Internship_Report_Template-2026.docx")
OUT = Path("/Users/madhavballabhkakkar/Downloads/FotoInsight_Internship_Report_Madhav_Ballabh_Kakkar.docx")


def set_para(paragraph, text: str) -> None:
    if paragraph.runs:
        paragraph.runs[0].text = text
        for run in paragraph.runs[1:]:
            run.text = ""
    else:
        paragraph.add_run(text)


def main() -> None:
    doc = Document(str(SRC))

    exact = {
        "Course Name (Course Code)": "Bachelor of Computer Application (BCA) – Internship / Project Work",
        "Month, YYYY": "November, 2026",
        "Paste Certificate Here": "[Paste Internship / Project Completion Certificate Here]",
        "<Mention details – max 15 lines>": (
            "I sincerely thank the School of Computer Application and Technology, Career Point University, Kota, "
            "for giving me the opportunity to complete this internship/project work. I am grateful to my project guides "
            "(Internal and External) for their continuous guidance, feedback, and encouragement throughout the development "
            "of FotoInsight. I also thank the faculty members who helped me understand data analytics concepts using Python, "
            "Pandas, and related tools. This project helped me learn how a real business workflow—from enquiry to booking, "
            "payment, and analytics—can be implemented as a complete web application with meaningful data insights. "
            "Finally, I thank my family and friends for their support during this work."
        ),
        "<Student Name>": "Madhav Ballabh Kakkar",
        "Place:                                                                                              ": (
            "Place: Kota                                                                                              "
        ),
        "Date:": "Date: 23 November 2026",
        "Online Deployment / Live Demo Link: _______________________________________________________": (
            "Online Deployment / Live Demo Link: https://fotoinsight.onrender.com/"
        ),
        "Home Page:": "Home Page: https://fotoinsight.onrender.com/ (paste screenshot below)",
        "A: Data Flow Diagram (DFD)": "A: Data Flow Diagram (DFD) – FotoInsight enquiry-to-analytics flow",
        "B: Entity Relationship Diagram (ERD)": "B: Entity Relationship Diagram (ERD) – FotoInsight SQLite schema",
        "C: Use Case Diagram (UCD)": "C: Use Case Diagram (UCD) – Visitor, Admin, Employee",
        "D: Data Dictionary (DD)": "D: Data Dictionary (DD) – Key tables/fields",
        "E: Screen Shots": "E: Screen Shots – Public site, Admin, Analytics, Data Sync",
    }

    by_heading = {
        "Introduction": (
            "This report presents FotoInsight, a photography-studio website and office analytics system developed during "
            "the internship/project work. The system combines a public website for clients with a secure admin/staff panel "
            "for managing customers, enquiries, bookings, payments, and projects. The analytics module uses Pandas and NumPy "
            "to calculate revenue, conversion, customer segments, seasonal demand, and service performance, and presents "
            "results through interactive charts. The work demonstrates an end-to-end data path from operational records to "
            "business insights suitable for academic evaluation and viva demonstration."
        ),
        "Background": (
            "The photography and event industry depends on timely follow-up of enquiries, clear booking schedules, "
            "accurate collection of advances and balances, and understanding of which services and seasons generate "
            "revenue. Many small studios still track these activities in scattered notes or spreadsheets, which makes "
            "conversion analysis and cash-based revenue reporting difficult. A data-science-oriented web system is relevant "
            "because it stores structured transactional data and then applies analytical rules (revenue from collected "
            "payments, conversion of worked enquiries, seasonal demand) to support decisions. FotoInsight addresses this "
            "domain with Flask, SQLite, Pandas/NumPy analytics, Chart.js visualizations, local JSON/CSV/Excel persistence, "
            "and optional Firebase Realtime Database REST synchronization."
        ),
        "Problem Statement": (
            "Problem: Studio owners need one system that (a) captures public enquiries, (b) manages bookings and payments "
            "without treating unpaid contracts as cash, and (c) explains business performance with transparent formulas. "
            "Why analytics is needed: Without consistent definitions for revenue and conversion, reports become misleading. "
            "Proposed solution: FotoInsight implements an office workflow in Flask with SQLite, computes analytics in "
            "Pandas/NumPy (revenue = paid/partially paid − refunds; conversion = converted ÷ eligible statuses), visualizes "
            "results with Chart.js, exports snapshots to JSON/CSV/Excel, and can sync to Firebase via REST. A supervised "
            "linear forecast (scikit-learn) is shown only when history and fit quality are sufficient."
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
            "This internship/project work was carried out under the School of Computer Application and Technology "
            "(SOCAT), Career Point University, Kota, as partial fulfilment of the BCA programme. The work focused on "
            "building a complete data-analytics-enabled web product for the photography-business domain."
        ),
        "About the Organization": (
            "Career Point University, Kota – School of Computer Application and Technology (SOCAT) provides academic "
            "guidance for student internship and project work in software development and data analytics. The present "
            "work was executed as a guided academic internship/project to design, implement, test, and deploy FotoInsight. "
            "[If you interned at an external company, replace this paragraph with the company name, nature of business, "
            "team size, and the department you joined.]"
        ),
        "Duration and Mode of the Internship": (
            "Duration: [Fill exact start and end dates as per your university letter], approximately as per BCA internship schedule.\n"
            "Mode: Hybrid / Remote development on macOS with cloud deployment on Render.\n"
            "Collaboration: GitHub repository and live hosted demo for guide/HOD review."
        ),
        "Role and Responsibilities During the Internship": (
            "Role: Data Analytics / Full-Stack Project Intern (Student Developer).\n"
            "Responsibilities: requirement analysis for studio workflows; database schema design; Flask route and model "
            "implementation; Pandas/NumPy analytics modules; Chart.js front-end charts; validation and security (sessions, "
            "CSRF); seed-data generation; testing of revenue/conversion rules; documentation; and deployment with Gunicorn "
            "on Render."
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
            "The week-wise plan is summarized in the table below (adjust dates to your actual internship calendar)."
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
            "[Paste selected code screenshots in Annexure E.]"
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
            "Empty custom ranges (e.g., 1990) correctly return zeros and an insufficient-data message rather than invented charts. "
            "Forecast may be withheld when R² is too low—this is intentional and viva-defensible.\n"
            "[Attach live Analytics screenshots with the exact numbers from the demo day.]"
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
            "student-configured project URL; Chart.js is used for visualization while meeting the charting objective."
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
            "Online Deployment / Live Demo Link: https://fotoinsight.onrender.com/\n"
            "Admin login for demo: admin / Admin@123\n"
            "Staff login for demo: employee / Employee@123"
        ),
        "Definitions, Acronyms, and Abbreviations": (
            "Key terms used in this report are defined in the abbreviation table below."
        ),
        "Conclusion": (
            "FotoInsight successfully demonstrates a data-analytics-oriented internship/project outcome: a working studio "
            "website and office system, transparent Pandas/NumPy analytics, visual charts, report exports, local "
            "JSON/CSV/Excel persistence, Firebase REST sync capability, and a live Render deployment. The project reinforces "
            "that reliable business insights depend as much on clear definitions and clean operational data as on algorithms. "
            "Key learning outcomes include full-stack Python development, analytics storytelling for viva, and cloud deployment practice."
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
            "11. Live demo – https://fotoinsight.onrender.com/"
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
        "<Guidelines: Show notebook/code execution screenshots, EDA visualizations, model training/evaluation outputs, and result visualizations.>": (
            "Insert screenshots: Home, Admin login, Analytics KPIs/charts, Data Sync export files, Firebase push result, Render live URL."
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
                "We hereby declare that this Project Report titled “FotoInsight – Photography Studio Website "
                "and Business Data Analytics System” submitted by us and approved by our project guide, the School "
                "of Computer Application and Technology (SOCAT), Career Point University, Kota, is our original work "
                "carried out during the internship/project period. The data used for analytics demonstration is "
                "synthetic demo data created for academic purposes and does not represent any real studio’s accounts.",
            )

    # Replace content under headings
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

    # Cover / declaration tables
    table0 = doc.tables[0]
    table0.rows[0].cells[0].text = (
        "GUIDE:\n"
        "Project Guide Name (External): [Fill External Guide Name]\n"
        "Designation: [Fill]\n"
        "Project Guide Name (Internal): [Fill Internal Guide Name]\n"
        "Designation: [Fill]"
    )
    table0.rows[0].cells[1].text = (
        "SUBMITTED BY:\n"
        "Madhav Ballabh Kakkar\n"
        "Student ID: [Fill University Roll / Enrollment No.]"
    )

    table1 = doc.tables[1]
    table1.rows[0].cells[1].text = "FotoInsight – Photography Studio Website and Business Data Analytics System"
    table1.rows[0].cells[2].text = "FotoInsight – Photography Studio Website and Business Data Analytics System"
    table1.rows[1].cells[1].text = "Madhav Ballabh Kakkar"
    table1.rows[1].cells[2].text = "Signature: _______________"
    table1.rows[3].cells[1].text = "[External Guide Name]"
    table1.rows[3].cells[2].text = "Signature: _______________"
    table1.rows[4].cells[1].text = "[Internal Guide Name]"
    table1.rows[4].cells[2].text = "Signature: _______________"

    # Week-wise table
    weeks = [
        ("Week 1", "[Dates]", "Domain study, requirement analysis, tech stack finalization (Flask, Pandas, SQLite)", "Understood studio workflow and project scope"),
        ("Week 2", "[Dates]", "Schema design, authentication, public website pages", "Built public site and secure login roles"),
        ("Week 3", "[Dates]", "Customers, enquiries, bookings, payments, projects modules", "Completed operational CRUD workflows"),
        ("Week 4", "[Dates]", "Pandas/NumPy analytics, Chart.js dashboards, report exports", "Delivered explainable business KPIs"),
        ("Week 5", "[Dates]", "JSON/CSV/Excel local persistence, Firebase REST sync, testing", "Met compulsory local + cloud sync requirements"),
        ("Week 6", "[Dates]", "Render deployment, documentation, viva preparation", "Published live demo and final report"),
    ]
    week_table = doc.tables[2]
    for row_index, row_data in enumerate(weeks, start=1):
        for col_index, value in enumerate(row_data):
            week_table.rows[row_index].cells[col_index].text = value

    # Repository artifacts table
    artifacts = doc.tables[3]
    artifacts.rows[1].cells[2].text = "GitHub: https://github.com/Madhavballabhkakkar/FotoInsight"
    artifacts.rows[2].cells[2].text = "GitHub commits / project progress notes"
    artifacts.rows[3].cells[2].text = "This filled report (Downloads / submitted softcopy)"
    artifacts.rows[4].cells[2].text = "GitHub repository + local tests/ folder"
    artifacts.rows[5].cells[2].text = "Live demo https://fotoinsight.onrender.com/ + certificate copy"

    # Abbreviations
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
    # ensure enough rows
    while len(abbr_table.rows) < len(abbreviations) + 1:
        abbr_table.add_row()
    for row_index, (abbr, desc) in enumerate(abbreviations, start=1):
        abbr_table.rows[row_index].cells[0].text = abbr
        abbr_table.rows[row_index].cells[1].text = desc

    # Data dictionary examples
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

    # Rename example captions near DD if present
    for paragraph in doc.paragraphs:
        if paragraph.text.strip() == "User Table (USR)":
            set_para(paragraph, "Users Table (users)")
        elif paragraph.text.strip() == "Supplier Table (SUPP)":
            set_para(paragraph, "Customers Table (customers)")

    # Brief about company footer area - find empty Normal after that heading-like footer
    # Already handled via About the Organization.

    doc.save(str(OUT))
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()
