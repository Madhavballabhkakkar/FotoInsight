"""Chapters 7 to 14 and Annexures A to C."""

D = "docs/report_assets/diagrams"
LIVE = "https://fotoinsight.onrender.com/"
REPO = "https://github.com/Madhavballabhkakkar/FotoInsight"


def build(r, A):
    # ------------------------------------------------------------------ 7 Advantages
    r.h1("Advantages of this Project")
    r.p(
        "The advantages of using a custom-made FotoInsight system for a photography studio, compared with spreadsheets, phone notes and "
        "general-purpose tools, are described below."
    )
    r.h2("Automation")
    r.p(
        "Every enquiry gets a reference code automatically, a repeated submit is recognised by its token without any staff effort, and "
        "converting an enquiry to a booking copies the customer, event and service details in one click. Totals, percentages, growth, "
        "customer segments and insight sentences are calculated by the program each time a page opens, so nobody has to maintain a "
        "spreadsheet formula. Reports in PDF, Excel and CSV and the local and Firebase copies are produced by one button each."
    )
    r.h2("Usability")
    r.p(
        "The public site and the staff area use a calm, uncluttered layout with large readable cards. Each KPI card carries a one-line "
        "explanation of what it counts, and the Analytics page starts with a section called How the numbers are defined. Search, filters and "
        "pagination are available on every list. The pages are responsive, so the owner can check numbers on a phone."
    )
    r.h2("Efficiency")
    r.p(
        "Pandas works on a few hundred rows, so the heaviest routes, the dashboard and the complete analytics, answered in under 40 "
        "milliseconds in the measurements of Chapter 6. SQLite needs no separate database server, so the application starts quickly and "
        "uses little memory on the free hosting plan. The whole project can be installed with one pip command and started with one Python command."
    )
    r.h2("Portability and Scalability")
    r.p(
        "All SQL is isolated in the model and analytics layers, and the MySQL-style statements are translated in one function. Moving "
        "to a larger server database later would mean changing the connection layer rather than every screen. The blueprint structure lets "
        "new modules, such as quotations or album orders, be added as a new route file, model file and template folder."
    )
    r.h2("Security")
    r.p(
        "Passwords are stored as hashes. The session cookie is signed, HttpOnly and SameSite Lax, and is marked Secure in production. "
        "Every change request must carry a CSRF token. Pages and APIs are guarded by login and role decorators, and employees are restricted "
        "to their own assigned records. All input is validated on the server, uploads are limited to 2 MB, SQL parameters are bound instead of "
        "pasted into the query, and errors are shown as clear messages without a stack trace."
    )
    r.h2("Honest Numbers and Availability")
    r.p(
        "Revenue is only money recorded in payments, conversion excludes untouched enquiries, and a forecast is hidden when the data cannot "
        "support it. Because the application is hosted on Render over HTTPS, the studio team and the owner can open it at any time from any "
        "device with a browser, without installing anything."
    )

    # ------------------------------------------------------------------ 8 Limitations
    r.h1("Limitations and Assumptions")
    r.p(
        "Every software system rests on a few operating assumptions and has technical limits. The assumptions and limitations of the "
        "current release of FotoInsight are listed here."
    )
    r.h2("Assumptions")
    r.p("The design of the platform relies on the following assumptions.")
    r.numbered(
        [
            ("Trusted studio staff", "The admin and employee accounts are created by the studio. Employees are trusted to enter correct data for the work assigned to them."),
            ("Money is recorded by staff", "The system does not connect to a payment gateway. Revenue is correct only when staff record each payment, refund and pending amount when it happens."),
            ("Demonstration data", "The records shown by the application are synthetic and were generated for the project. The real studio data would need to be imported and checked before the numbers are used for decisions."),
            ("Reliable internet and a modern browser", "Visitors and staff use a current browser with JavaScript and cookies enabled. Charts need JavaScript."),
            ("Configuration is maintained", "The deployment assumes that SECRET_KEY, SQLITE_PATH and, if the cloud copy is used, FIREBASE_DB_URL and FIREBASE_AUTH_TOKEN are set correctly in the hosting dashboard."),
        ]
    )
    r.h2("Limitations")
    r.p("The current release has the following limitations.")
    r.numbered(
        [
            ("SQLite allows one writer", "SQLite accepts one write at a time, so Gunicorn runs with one worker. This is enough for a small studio but not for many simultaneous editors."),
            ("Free hosting limits", "The Render free service sleeps when idle, so the first request after a pause is slow. The SQLite file is created again at each build, so records added on the live site are not kept across deployments. A paid plan with a persistent disk or a hosted database would be needed for real use."),
            ("Synthetic demonstration data", "All results in this report come from generated data. The forecast is therefore hidden, and revenue, conversion and segment numbers describe the sample and not a real studio."),
            ("No online payments, invoices or client login", "Clients cannot pay, sign in or see their booking online, and no e-mail or SMS is sent automatically."),
            ("Simple forecast only", "The forecast is a straight line through monthly values. It cannot see festivals, seasons or growth that is not linear, and it is hidden when R squared is below 0.15."),
            ("Local folder is temporary on the cloud", "The data folder written by the Data Sync page lives on the hosting disk. It is useful for download and for the Firebase push, but it is not a backup."),
            ("Firebase needs the owner's database", "The cloud copy works only after the studio creates a Firebase Realtime Database and sets its address. Without it the button returns a clear message that Firebase is not configured."),
            ("No multi-language or accessibility audit", "The interface is in English. Basic semantic HTML and Bootstrap accessibility are used, but a full accessibility test was not done."),
        ]
    )

    # ------------------------------------------------------------------ 9 Future scope
    r.h1("Future Scope and Further Enhancement of the Project")
    r.p(
        "The FotoInsight platform is built as a modular Flask application, so new features can be added without rewriting the existing code. "
        "The most useful enhancements are described below."
    )
    r.h2("Persistent Production Database")
    r.p(
        "Moving the data to a hosted PostgreSQL or MySQL database, or to a Render disk, would keep records between deployments and allow several "
        "workers. Because the SQL is concentrated in the model layer and normalised in one function, this change is mostly limited to the "
        "connection code and the schema file."
    )
    r.h2("Real Studio Data Import and Backups")
    r.p(
        "A CSV import screen with validation and a preview would let the studio load its real customers, bookings and payments. Scheduled "
        "exports to cloud storage would add automatic backups to the manual Data Sync buttons."
    )
    r.h2("Client Portal and Online Payments")
    r.p(
        "Clients could log in to view their booking, team, payment balance and project status, download delivered albums and pay the next "
        "instalment through a payment gateway. Each payment would create a payment row automatically and use the same signed revenue rule."
    )
    r.h2("Notifications and Calendar")
    r.p(
        "E-mail or WhatsApp reminders for follow-ups, upcoming events and delivery dates would help the team act on the numbers. A shared "
        "calendar view of events and team availability would prevent double booking of photographers."
    )
    r.h2("Deeper Analytics")
    r.p(
        "With real data covering several years, seasonal models, customer lifetime value, lead-source performance and cohort analysis can be "
        "added. The forecast could use a seasonal method and show a prediction interval, but it would keep the same rule of staying hidden when "
        "the history does not support it."
    )
    r.h2("Progressive Web App and Mobile Companion")
    r.p(
        "The staff screens could be turned into an installable web app that works on weak networks, so photographers can update project status "
        "and add notes from the event location."
    )

    # ------------------------------------------------------------------ 10 Repository
    r.h1("Project Repository Location")
    r.p(
        "The complete source code (app/, database/, tests/, docs/, the Render blueprint render.yaml and the deployment notes) is on GitHub at "
        f"{REPO} (branch: main). The softcopy deliverables, test artefacts and the internship completion certificate are in a shared Google "
        "Drive folder ([Insert Shared Google Drive Root Folder Link]). Both locations are shared with my Internal Project Guide and the Head "
        "of Department (SOCA), Career Point University, Kota."
    )
    r.table_caption("Project Artifacts and Their Location")
    r.table(
        ["S#", "Project Artifacts (softcopy)", "Location (Folder Name, Drive Link etc.)", "Verified by Project Guide", "Verified by HOD"],
        [
            ["1", "Project Synopsis Report (Final Version)", "Google Drive: /Jayanti_Jha_K25341_CAC771/01_Synopsis ([Insert Drive Link])", "Ms. Namrata Kashyap\n__________", "Dr. Garima Tyagi\n__________"],
            ["2", "Project Progress updates", f"Google Drive: /Jayanti_Jha_K25341_CAC771/02_Progress_Updates ([Insert Drive Link]); GitHub Commit History (main): {REPO}", "Ms. Namrata Kashyap\n__________", "Dr. Garima Tyagi\n__________"],
            ["3", "Project Report (Final Version)", "Google Drive: /Jayanti_Jha_K25341_CAC771/03_Final_Report ([Insert Drive Link])", "Ms. Namrata Kashyap\n__________", "Dr. Garima Tyagi\n__________"],
            ["4", "Source code and database scripts", f"{REPO} (app/, database/, tests/, render.yaml)", "Ms. Namrata Kashyap\n__________", "Dr. Garima Tyagi\n__________"],
            ["5", "Internship Completion Certificate", "Google Drive: /Jayanti_Jha_K25341_CAC771/04_Certificate ([Insert Drive Link])", "Ms. Namrata Kashyap\n__________", "Dr. Garima Tyagi\n__________"],
        ],
        [600, 2000, 3500, 1750, 1774],
        size=22,
        center_cols=(0,),
    )

    # ------------------------------------------------------------------ 11 Deployment
    r.h1("Online Deployment Link")
    r.p_with_links(["Online Deployment / Live Demo Link: ", (LIVE, LIVE)])
    r.p(
        "This photography studio website and analytics dashboard for Fotographiya is hosted in the cloud on Render and does not have to be "
        "installed on a local computer. The public pages are open to everyone. The staff area is reached through /admin/login and is "
        "available only to the seeded admin and employee accounts. The database is a SQLite file created during the build, and the optional "
        "cloud copy is stored in a Firebase Realtime Database when the owner configures it."
    )
    r.table_caption("Deployment Components and Resource Identifiers")
    r.table(
        ["Component / Tier", "Cloud Service", "Live URL / Resource Identifier"],
        [
            ["Public website, staff dashboard and JSON API", "Render web service (free plan, Python 3.12.8, Gunicorn with 1 worker)", LIVE],
            ["Health check", "Render health check path", LIVE + "health"],
            ["Staff login page", "Flask route /admin/login", LIVE + "admin/login"],
            ["Source repository and build trigger", "GitHub, branch main", REPO],
            ["Database", "SQLite file created by the build command", "instance/fotoinsight.db (path set by SQLITE_PATH)"],
            ["Optional cloud copy", "Firebase Realtime Database (REST PUT and GET)", "Node fotoinsight.json under FIREBASE_DB_URL (set by the owner)"],
        ],
        [2800, 3300, 3524],
        size=22,
    )

    # ------------------------------------------------------------------ 12 Abbreviations
    r.h1("Definitions, Acronyms, and Abbreviations")
    r.p("The abbreviations used in this report are listed below in alphabetical order.")
    abbr = [
        ("API", "Application Programming Interface. The /api/... routes that send and receive JSON between the browser and the Flask server."),
        ("BCA", "Bachelor of Computer Application."),
        ("CMS", "Content Management System."),
        ("CRM", "Customer Relationship Management. Keeping customers, enquiries and bookings in one system."),
        ("CRUD", "Create, Read, Update and Delete. The four basic record operations."),
        ("CSRF", "Cross-Site Request Forgery. An attack that makes a signed-in browser send an unwanted request. FotoInsight blocks it with a token."),
        ("CSS", "Cascading Style Sheets. The styling language of web pages."),
        ("CSV", "Comma-Separated Values. A plain-text table file that opens in Excel."),
        ("DB", "Database."),
        ("DFD", "Data Flow Diagram. A diagram of how data moves between entities, processes and data stores."),
        ("ERD", "Entity-Relationship Diagram. A diagram of tables and the relationships between them."),
        ("FK", "Foreign Key. A column that refers to the primary key of another table."),
        ("GB", "Gigabyte."),
        ("GHz", "Gigahertz."),
        ("HTML", "HyperText Markup Language. The structure of a web page."),
        ("HTTP", "HyperText Transfer Protocol."),
        ("HTTPS", "HTTP over TLS. The encrypted form used by the live site."),
        ("IDE", "Integrated Development Environment. The code editor used to write the project."),
        ("INR", "Indian Rupee."),
        ("JSON", "JavaScript Object Notation. The text format used by the APIs and the local export."),
        ("KPI", "Key Performance Indicator. A headline number such as total revenue or conversion rate."),
        ("NumPy", "Numerical Python. The library used for calculations on arrays."),
        ("ORM", "Object-Relational Mapping. Not used in this project, which uses plain SQL."),
        ("PDF", "Portable Document Format. One of the three report formats."),
        ("PK", "Primary Key. The column that identifies a row in a table."),
        ("R squared", "Coefficient of determination (R²). A number from 0 to 1 that tells how well a straight line fits the data. A forecast is hidden below 0.15."),
        ("RAM", "Random Access Memory."),
        ("REST", "Representational State Transfer. The style of HTTP API used for the Firebase copy and the JSON routes."),
        ("SDLC", "Software Development Life Cycle."),
        ("SOCA", "School of Computer Application and Technology, Career Point University, Kota."),
        ("SQL", "Structured Query Language."),
        ("SQLite", "A file-based relational database engine bundled with Python."),
        ("SSD", "Solid State Drive."),
        ("UCD", "Use Case Diagram."),
        ("UI", "User Interface."),
        ("UK", "Unique Key. A column whose values cannot repeat."),
        ("UPI", "Unified Payments Interface. One of the payment methods stored with a payment."),
        ("URL", "Uniform Resource Locator. A web address."),
        ("WSGI", "Web Server Gateway Interface. The standard that connects Gunicorn to Flask."),
        ("XSS", "Cross-Site Scripting. Injecting a script into a page. Jinja2 escapes output by default to prevent it."),
    ]
    r.table_caption("Abbreviations Used in This Report")
    r.table(["Abbreviation", "Description"], [[a, b] for a, b in abbr], [1666, 7958], size=22, bold_first=True)

    # ------------------------------------------------------------------ 13 Conclusion
    r.h1("Conclusion")
    r.p(
        "During the 45-day Data Analyst internship at Fotographiya Ventures Pvt. Ltd., Kota, I built FotoInsight, a photography studio "
        f"website with a staff dashboard and an analytics section, available now at {LIVE}. The system consists of the following modules: "
        "the public website with Home, About, Services, Portfolio, Contact and Enquiry pages; the customer, enquiry, booking, payment and "
        "project management screens with admin and employee roles; the Pandas and NumPy analytics with plain-language insights and a "
        "guarded forecast; and the report, export and Firebase copy tools."
    )
    r.p(
        "Testing was done, and the results can be summarised as follows. All six automated tests passed. A repeated enquiry submit returned "
        "the same reference code. A request without a CSRF token returned 400, an API call without login returned 401, a payment above the "
        "contract balance returned 409 and a body above 2 MB returned 413. The revenue rule was proved with a known case: a contract of INR "
        "100000 with INR 30000 paid, INR 70000 pending and INR 5000 refunded gave net revenue of INR 25000. On the live demonstration "
        "data, the overview showed collected revenue of INR 19,91,860.15 and a conversion rate of 53.4 percent for 2026, and the forecast "
        "was correctly hidden because the straight line explained almost none of the history (R squared 0.00 and 0.01). The heaviest "
        "routes answered in under 40 milliseconds in the local measurement."
    )
    r.p(
        "Working under the supervision of my External Guide Mr. Ajay Raj Kushwah and my Internal Guide Ms. Namrata Kashyap, I worked "
        "through the full development cycle: requirement analysis, database design, coding in five build phases, integration, testing, "
        "deployment and handover, with version control on Git and GitHub. The most useful part of the experience was solving real "
        "problems: a revenue figure that counted contracts instead of cash, a double-clicked form that created two enquiries, a forecast "
        "drawn over data without a trend, a database that a free host could not provide, and an empty site after the first release."
    )
    r.p(
        "For Fotographiya Ventures Pvt. Ltd., the platform shows how enquiries, bookings, payments and projects can live in one place and how "
        "the numbers can be defined clearly and explained to the owner. The modular design allows the real data, a persistent database, "
        "a client portal and online payments to be added later without rebuilding the system."
    )

    # ------------------------------------------------------------------ 14 References
    r.h1("References")
    r.p(
        "The references listed below identify the project sources, official framework and library documentation, the hosting guides and "
        "the security guidance consulted during the internship and the Render deployment of FotoInsight."
    )
    refs = [
        'Fotographiya Ventures Pvt. Ltd., "Fotographiya Official Website," Kota, 2026. Available: https://www.fotographiya.com/ (Accessed: November 2026).',
        f'"FotoInsight Source Code Repository (branch: main)," GitHub, 2026. Available: {REPO} (Accessed: November 2026).',
        f'"FotoInsight Live Web Application," Render, 2026. Available: {LIVE} (Accessed: November 2026).',
        'Pallets Projects, "Flask Documentation," Version 3.1, Pallets, 2026. Available: https://flask.palletsprojects.com/ (Accessed: November 2026).',
        'Pallets Projects, "Jinja Template Designer Documentation," Pallets, 2026. Available: https://jinja.palletsprojects.com/ (Accessed: November 2026).',
        'Pallets Projects, "Werkzeug: Utilities, Password Hashing," Pallets, 2026. Available: https://werkzeug.palletsprojects.com/ (Accessed: November 2026).',
        'SQLite Consortium, "SQLite Documentation," SQLite, 2026. Available: https://www.sqlite.org/docs.html (Accessed: November 2026).',
        'Python Software Foundation, "sqlite3: DB-API 2.0 Interface for SQLite Databases," Python 3 Documentation, 2026. Available: https://docs.python.org/3/library/sqlite3.html (Accessed: November 2026).',
        'pandas Development Team, "pandas Documentation," Version 3.1, 2026. Available: https://pandas.pydata.org/docs/ (Accessed: November 2026).',
        'NumPy Developers, "NumPy Reference," Version 2.5, 2026. Available: https://numpy.org/doc/stable/ (Accessed: November 2026).',
        'scikit-learn Developers, "LinearRegression," scikit-learn User Guide, 2026. Available: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LinearRegression.html (Accessed: November 2026).',
        'scikit-learn Developers, "r2_score," scikit-learn API Reference, 2026. Available: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.r2_score.html (Accessed: November 2026).',
        'Chart.js Contributors, "Chart.js Documentation," Version 4.4, 2026. Available: https://www.chartjs.org/docs/latest/ (Accessed: November 2026).',
        'Bootstrap Authors, "Bootstrap Documentation," Version 5.3, 2026. Available: https://getbootstrap.com/docs/5.3/ (Accessed: November 2026).',
        'Gunicorn Contributors, "Gunicorn: Python WSGI HTTP Server for UNIX," 2026. Available: https://gunicorn.org/ (Accessed: November 2026).',
        'Render Services, Inc., "Deploy a Flask App on Render," Render Docs, 2026. Available: https://render.com/docs/deploy-flask (Accessed: November 2026).',
        'Render Services, Inc., "Blueprint Specification (render.yaml)," Render Docs, 2026. Available: https://render.com/docs/blueprint-spec (Accessed: November 2026).',
        'Render Services, Inc., "Health Checks," Render Docs, 2026. Available: https://render.com/docs/health-checks (Accessed: November 2026).',
        'Google LLC, "Firebase Realtime Database REST API," Firebase Documentation, 2026. Available: https://firebase.google.com/docs/database/rest/start (Accessed: November 2026).',
        'py-pdf Contributors, "fpdf2 Documentation," 2026. Available: https://py-pdf.github.io/fpdf2/ (Accessed: November 2026).',
        'OpenPyXL Contributors, "openpyxl Documentation," 2026. Available: https://openpyxl.readthedocs.io/ (Accessed: November 2026).',
        'pytest Contributors, "pytest Documentation," Version 9.2, 2026. Available: https://docs.pytest.org/ (Accessed: November 2026).',
        'OWASP Foundation, "Cross-Site Request Forgery Prevention Cheat Sheet," OWASP Cheat Sheet Series, 2026. Available: https://cheatsheetseries.owasp.org/cheatsheets/Cross-Site_Request_Forgery_Prevention_Cheat_Sheet.html (Accessed: November 2026).',
        'A. Barth, "HTTP State Management Mechanism," RFC 6265, Internet Engineering Task Force, April 2011. Available: https://www.rfc-editor.org/info/rfc6265 (Accessed: November 2026).',
        'M. Fowler, "Patterns of Enterprise Application Architecture," Addison-Wesley, 2002 (for data flow and layered design concepts).',
    ]
    for i, ref in enumerate(refs, 1):
        r.p(f"[{i}] {ref}")

    # ------------------------------------------------------------------ Annexure A
    r.annex("A", "Data Flow Diagram (DFD)")
    r.p(
        "This annexure details the Level-0 Context Diagram (refer Figure 3.1), the Level-1 Data Flow Diagram and five Level-2 diagrams. "
        "The Level-1 diagram (Figure A.1) splits the system into six main processes. Level-2 diagrams then open the processes that "
        "contain the most important rules: authentication (1.0), enquiry capture and conversion (2.0 and 3.0), payments and revenue "
        "(4.0), analytics (5.0) and reports and sync (6.0). Symbols follow the usual convention: a rounded box is a process, an open "
        "rectangle with a tag is a data store, a plain rectangle is an external entity and an arrow is a data flow."
    )
    r.figure(f"{D}/04_dfd_level1.png", "Level-1 Data Flow Diagram of the FotoInsight Studio Platform", 6.0)
    r.p(
        "Input comes from three places: the studio staff, the visitor and the system clock through the chosen date range. Processes "
        "1.0 and 2.0 deal with identity and with public input. Processes 3.0 and 4.0 maintain the main records, process 5.0 only reads "
        "them, and process 6.0 reads them again to write files and the cloud copy. Data stores D1 to D6 are the users table, the customer "
        "and enquiry tables, the booking, team and project tables, the payment table, the service and settings tables, and the files."
    )
    r.figure(f"{D}/08_dfd_l2_auth.png", "Level-2 Data Flow Diagram - Authentication, CSRF Check, Session and Role Gate", 6.2)
    r.p(
        "A login form first meets the CSRF check (1.1). A missing or wrong token stops the request with HTTP 400. The server then looks up the "
        "username in D1 and compares the password hash (1.2); a mismatch or an inactive user returns 401. On success (1.3) the old "
        "session is cleared and a new one is created with a fresh CSRF value, the user id, the role and the employee id, and the browser is "
        "redirected to the dashboard. Process 1.4 then examines every later request and returns 401 when there is no session and 403 when "
        "the role is not allowed."
    )
    r.figure(f"{D}/09_dfd_l2_enquiry.png", "Level-2 Data Flow Diagram - Public Enquiry Capture, Status Workflow and Conversion to Booking", 6.2)
    r.p(
        "The enquiry form is cleaned and validated (2.1), then the submission token is looked up in D2 (2.2). A known token returns the "
        "existing reference code, and an unknown token leads to the creation of a customer link and an enquiry code (2.3), which are "
        "stored and returned with HTTP 201. Inside the staff area, an admin can assign an employee, anyone allowed can add notes (3.1), "
        "the status is updated (3.2), and the admin can convert the enquiry to a booking once (3.3). A repeat attempt returns 409 because "
        "bookings.enquiry_id is unique."
    )
    r.figure(f"{D}/10_dfd_l2_payments.png", "Level-2 Data Flow Diagram - Payments, Balance Check and Signed Revenue Rule", 6.2)
    r.p(
        "A payment form is validated (4.1) and compared with the contract value of the booking (4.2). A payment that would take the total "
        "above the contract is refused with 409. Accepted payments are inserted into D4 (4.3). Process 4.4 reads all rows and applies the "
        "signed revenue rule: paid and partially paid add the amount, refunded subtracts it and pending adds nothing. The result feeds the "
        "Payments page (collected, refunds, net revenue and outstanding) and the analytics engine."
    )
    r.figure(f"{D}/11_dfd_l2_analytics.png", "Level-2 Data Flow Diagram - Analytics Pipeline with Pandas, NumPy and the Forecast Guard", 6.2)
    r.p(
        "The chosen date range is resolved (5.1) and the business tables are read from the database into Pandas frames (5.2). NumPy "
        "calculates the metrics (5.3): revenue from signed amounts, conversion rate, customer segments, service, location and seasonal tables "
        "and growth against the previous period. The monthly series goes to the forecast guard (5.4), which either returns a prediction or a "
        "message that explains why none is shown. Process 5.5 writes the insight sentences and returns one JSON document to Chart.js."
    )
    r.figure(f"{D}/12_dfd_l2_sync.png", "Level-2 Data Flow Diagram - Reports, Local Export and Firebase Sync", 6.2)
    r.p(
        "Only the admin can reach these processes. A report request is checked (6.1) and the file is built from the business tables as PDF, "
        "Excel or CSV (6.2). A sync request first writes the six main tables to JSON, CSV and Excel files and one bundle in the data folder "
        "(6.3), then sends the bundle to Firebase with a REST PUT (6.4). A second button reads the cloud copy back with a REST GET and shows row "
        "counts, table names and the last sync time (6.5)."
    )
    r.table_caption("Process Summary Table")
    r.table(
        ["Process ID & Name", "Primary User / System Input", "Core Application Processing", "Data Stores Accessed", "Primary Output"],
        [
            ["1.0 Authentication, CSRF and Session Control", "Username, password and CSRF token from staff; session cookie on later requests", "Token check, password hash comparison, session creation with role and employee id, role gate on every request", "D1 Users and employees", "Session cookie, HTTP 400, 401 or 403, redirect to the dashboard or the login page"],
            ["2.0 Public Enquiry and Contact Capture", "Enquiry or contact form with a submission token from the visitor", "Field validation, duplicate check by token, customer link, enquiry code creation", "D2 Customers, enquiries and notes", "Reference code with 201, or the same code with duplicate true"],
            ["3.0 CRM Records", "Create, edit, search, assign, note, status and convert requests from staff", "Validation, employee scope filter, status updates, once-only conversion to a booking, team assignment", "D2, D3 Bookings, team and projects, D5 Services and settings", "Lists, detail pages, 409 on a repeated conversion"],
            ["4.0 Payments and Project Tracking", "Payment and project forms from the admin; status and notes from employees", "Amount, date and method validation, balance check, signed revenue rule, project status rules", "D3, D4 Payments", "Payment list, net revenue, collected, refunds, outstanding amount, project list"],
            ["5.0 Analytics Engine", "Date range from the staff screen", "Pandas loading, NumPy metrics, segment rules, forecast guard, insight sentences", "D2, D3, D4, D5 (read only)", "JSON with KPIs, charts, insights and forecast or a hidden-forecast message"],
            ["6.0 Reports, Export and Cloud Sync", "Report type, range and format; sync requests from the admin", "Report building with fpdf2 and openpyxl, JSON, CSV and Excel export, Firebase REST PUT and GET", "D2 to D5 (read), D6 Local files and Firebase copy", "PDF, Excel or CSV file, local files, sync status and row counts"],
        ],
        [1606, 1842, 2633, 1559, 1984],
        size=20,
        header_size=22,
    )

    # ------------------------------------------------------------------ Annexure B
    r.annex("B", "Entity-Relationship Diagram (ERD)")
    r.p(
        "The following annexure describes the Entity-Relationship Diagram that represents the structure of the SQLite database. The "
        "database has 13 tables created by database/schema_sqlite.sql. Foreign keys are switched on for every connection "
        "(PRAGMA foreign_keys = ON), so the relationships below are enforced by the database engine."
    )
    r.figure(f"{D}/05_erd.png", "Entity-Relationship Diagram (ERD) of the FotoInsight SQLite Database", 4.9, 8.3)
    r.p(
        "Each enquiry stores its customer in customer_id, each booking stores its customer, service and optional package, each payment "
        "stores its booking and the user who recorded it, and each project stores its booking, photographer and editor. The columns "
        "bookings.enquiry_id and projects.booking_id are unique, which makes the relationships one to at most one. The delete rules are "
        "chosen to protect history: a customer or service that is still used cannot be deleted (RESTRICT), while dependent notes, "
        "team rows, payments and projects are removed together with their booking or enquiry (CASCADE) and optional links are cleared (SET NULL)."
    )
    r.figure(f"{D}/13_status_lifecycles.png", "Status Lifecycles of Enquiries, Bookings, Projects and Payments", 6.0, 7.5)
    r.p(
        "The status columns hold short codes defined in app/constants.py. The conversion rate uses the enquiry statuses, the booking and "
        "project screens use the booking and project statuses, and the revenue rule uses the payment statuses. The sign shown under each "
        "payment status is the one that Pandas applies when it adds the signed amount to the payment rows."
    )
    r.table_caption("Entity Relationship and Cardinality Summary")
    r.table(
        ["Entity Pair", "Cardinality", "Linking Column and Delete Rule", "Functional Purpose"],
        [
            ["employees -> users", "1 : N (optional)", "users.employee_id, ON DELETE SET NULL", "Links a login to a staff member; the admin login has no employee"],
            ["customers -> enquiries", "1 : N (optional)", "enquiries.customer_id, ON DELETE RESTRICT", "Shows all enquiries of one customer"],
            ["customers -> bookings", "1 : N", "bookings.customer_id, ON DELETE RESTRICT", "A customer with bookings cannot be deleted"],
            ["enquiries -> bookings", "1 : 0..1", "bookings.enquiry_id (UNIQUE), ON DELETE RESTRICT", "Allows conversion only once"],
            ["enquiries -> enquiry_notes", "1 : N", "enquiry_notes.enquiry_id, ON DELETE CASCADE", "Keeps the call and follow-up history"],
            ["users -> enquiry_notes", "1 : N", "enquiry_notes.user_id, ON DELETE RESTRICT", "Records who wrote each note"],
            ["services -> packages", "1 : N", "packages.service_id, ON DELETE RESTRICT", "Packages belong to one service"],
            ["services -> bookings", "1 : N", "bookings.service_id, ON DELETE RESTRICT", "Service performance analysis"],
            ["bookings -> booking_team", "1 : N", "booking_team.booking_id, ON DELETE CASCADE; UNIQUE (booking, employee, role)", "Assigns employees with a role to a booking"],
            ["bookings -> payments", "1 : N", "payments.booking_id, ON DELETE CASCADE", "Builds the paid, refunded and outstanding amounts"],
            ["bookings -> projects", "1 : 0..1", "projects.booking_id (UNIQUE), ON DELETE CASCADE", "One delivery project per booking"],
            ["employees -> enquiries", "1 : N (optional)", "enquiries.assigned_employee_id, ON DELETE SET NULL", "Shows which staff member follows up an enquiry"],
            ["employees -> booking_team", "1 : N", "booking_team.employee_id, ON DELETE RESTRICT", "A staff member with assignments cannot be deleted"],
            ["employees -> projects", "1 : N", "projects.photographer_id and editor_id, ON DELETE SET NULL", "Shows who shoots and who edits"],
            ["customers -> customer_feedback", "1 : N", "customer_feedback.customer_id, ON DELETE CASCADE", "Ratings from 1 to 5 with a comment"],
        ],
        [2000, 1400, 3300, 2924],
        size=20,
        header_size=22,
    )

    # ------------------------------------------------------------------ Annexure C
    r.annex("C", "Use-Case Diagram (UCD)")
    r.p(
        "The model described in this annexure is used to illustrate the relationship between the actors of the FotoInsight platform and "
        "the functions that each of them can perform."
    )
    r.figure(f"{D}/06_use_case_diagram.png", "UML Use-Case Diagram of the FotoInsight Studio Platform", 5.4, 8.3)
    r.p(
        "The visitor does not need to sign in. Submitting an enquiry is extended by the duplicate protection that uses the submission token. "
        "Every use case in the staff area includes UC-04, because the login gate stands in front of all of them. The employee can do "
        "UC-05 to UC-09 only on the work assigned to him or her. The admin is also an employee in the diagram, so the admin inherits "
        "these use cases and adds UC-10 to UC-15."
    )
    r.table_caption("Actor and Use-Case Summary")
    r.table(
        ["Use Case ID", "Use Case Name", "Primary / Secondary Actor", "Precondition and Interaction Summary"],
        [
            ["UC-01", "Browse Studio Pages", "Visitor", "No login needed. The visitor opens Home, About, Services and Portfolio and sees services, packages and prices from the database."],
            ["UC-02", "Submit Event Enquiry", "Visitor", "The visitor fills the enquiry form. The server validates it, checks the submission token and returns a reference code. A repeat returns the same code."],
            ["UC-03", "Send Contact Message", "Visitor", "The visitor sends name, e-mail, phone and message. The message is stored as an enquiry with the source contact."],
            ["UC-04", "Log In and Log Out", "Employee, Admin", "The user opens /admin/login with a valid username and password. A session cookie is created. Logout clears the session."],
            ["UC-05", "View Overview and Search", "Employee, Admin", "After login the user sees KPI cards, insight lines, charts and a global search box. Employees see only their own scope."],
            ["UC-06", "View and Edit Customers", "Employee, Admin", "The user lists, searches and opens customers. An employee sees customers linked to assigned work."],
            ["UC-07", "View Enquiries, Update Status, Add Notes", "Employee, Admin", "The user opens an enquiry, changes its status and adds a note. The admin sees all enquiries."],
            ["UC-08", "View Bookings and Calendar", "Employee, Admin", "The user opens the booking list, detail and calendar. Employees see bookings where they are in the team."],
            ["UC-09", "Track Projects", "Employee, Admin", "An employee may change only the status and notes of an assigned project. Other fields return 403."],
            ["UC-10", "Create, Assign, Convert and Delete Records", "Admin", "The admin creates and edits customers, enquiries, bookings and projects, assigns an enquiry and converts it once to a booking."],
            ["UC-11", "Record and Edit Payments", "Admin", "The admin enters amount, date, method, status and reference. A payment above the contract balance returns 409."],
            ["UC-12", "View Analytics, Insights and Forecast", "Admin", "The admin chooses a date range and reads definitions, charts, insights and the forecast or its hidden-forecast message."],
            ["UC-13", "Download Reports", "Admin", "The admin chooses one of six reports and a format (PDF, Excel or CSV) and a date range."],
            ["UC-14", "Export Files and Sync to Firebase", "Admin, Firebase", "The admin writes the local files and pushes the bundle to the Firebase Realtime Database or reads the summary back."],
            ["UC-15", "Manage Services, Packages, Settings and Logins", "Admin", "The admin edits services, packages, business details, employee records and employee logins."],
        ],
        [1000, 2400, 1700, 4524],
        size=20,
        header_size=22,
        center_cols=(0,),
    )
