"""Chapters 4 to 6."""

D = "docs/report_assets/diagrams"


def build(r, A):
    # ------------------------------------------------------------------ 4 Implementation
    r.h1("Implementation Methodology")
    r.p(
        "The project followed a structured, iterative approach with seven stages, as shown in Figure 4.1. The work was divided into "
        "small steps, and each step was tested before the next one started. The stages were:"
    )
    r.numbered(
        [
            ("Requirement Analysis (Days 1 to 4)", "Study of the studio workflow from enquiry to delivery. List of the data to be tracked and the questions the owner wants answered. Written definitions of revenue and conversion rate."),
            ("System Design (Days 5 to 9)", "Thirteen-table schema with keys and check rules, route list for 13 blueprints, rules for each analytics number, screen list for the public site and the dashboard, and a role table for admin and employee."),
            ("Iterative Coding (Days 10 to 36)", "Modules were developed one at a time in five build phases: foundation and public site, customers and enquiries, bookings, payments and projects, analytics, and reports with data sync."),
            ("Integration (Days 37 to 39)", "Blueprints, models, the Pandas layer and the Chart.js screens were joined. The JSON API for the dashboard was connected to the charts and the insight sentences."),
            ("Testing and Debugging (Days 40 to 45)", "Six pytest tests, manual security checks, response-time checks and bug fixing. Defects found here returned to coding through the feedback loop in the flowchart."),
            ("Deployment", "After handover, the application was deployed on Render with a build command that creates and seeds the SQLite database, a Gunicorn start command and a /health check."),
            ("Maintenance", "Data export, Firebase copy and rule updates continue after deployment."),
        ]
    )
    r.figure(f"{D}/03_sdlc_flowchart.png", "SDLC and Production Deployment Flowchart for FotoInsight", 6.2)
    r.p(
        "The flowchart shows the seven stages in order. The dashed arrow is the feedback loop: defects found during testing go back to "
        "coding, and only then do the changes move forward again. The dashed arrow after maintenance leads to the handover of the "
        "working application, the source code and this report."
    )
    r.figure(f"{D}/04_dfd_level1.png", "Level-1 Data Flow Diagram (DFD) of FotoInsight", 6.1)
    r.p(
        "The studio staff sign in through process 1.0, which checks the password and loads the role from the users table (D1). "
        "Visitors reach process 2.0, which stores a new enquiry and customer in D2 and returns a reference code. Process 3.0 handles "
        "customers, enquiries, bookings and services, process 4.0 handles payments and projects, process 5.0 reads the business tables "
        "to build analytics for a chosen date range, and process 6.0 produces reports and the local and Firebase copies (D6)."
    )
    r.figure(f"{D}/05_erd.png", "Entity-Relationship Diagram (ERD) of the 13 SQLite Tables", 4.9, 8.3)
    r.p(
        "One customer can have many enquiries and many bookings. One enquiry can become at most one booking, because bookings.enquiry_id "
        "is unique. One booking can have many payments and many team members, and at most one project, because projects.booking_id is "
        "unique. A service has many packages and many bookings. An employee can be linked to one user login and can be assigned to "
        "enquiries, bookings and projects."
    )
    r.figure(f"{D}/06_use_case_diagram.png", "Use Case Diagram of the FotoInsight Platform", 5.4, 8.3)
    r.p(
        "The visitor only reads the website and sends forms. The employee works inside the staff area on assigned records. The admin "
        "controls everything the employee can do and also the records, payments, analytics, reports, data sync and settings."
    )
    r.h2("Domain-Specific Implementation Details")
    r.p(
        "The project combined web development, relational database design, data analysis and cloud deployment. The main decisions "
        "in each area are described below."
    )
    r.h3("Web Application Development")
    num = r._new_num(13)
    for lead, body in [
        ("Front End (HTML, CSS, JavaScript, Jinja2, Bootstrap, Chart.js)", "The public site and the staff screens are server-rendered Jinja2 templates (35 template files) with the base layouts public/base.html and admin/base.html. Bootstrap 5.3.3 and Chart.js 4.4.1 are stored in static/vendor, so the pages work without a CDN. Four small JavaScript files (api.js, dashboard.js, analytics.js, public.js) fetch JSON, draw charts and send forms. api.js adds the X-CSRF-Token header to every change request."),
        ("Back-end development with Flask", "create_app() in app/__init__.py registers 13 blueprints, the database teardown, the CSRF and login hooks, template filters (INR formatting and status labels) and error handlers for 400, 401, 403, 404, 409, 413 and 500. About 6400 lines of Python (application, seed script and tests) are organised as routes, models, validators, analytics, reports and sync modules."),
        ("SQLite database connectivity", "app/db.py opens one sqlite3 connection per request, turns foreign keys on and returns rows as dictionaries. The queries were first written in MySQL style (%s placeholders, DATE_FORMAT, YEAR, MONTH, CURDATE), so normalize_sql() translates them to SQLite when they run. The schema file schema_sqlite.sql creates 13 tables with primary keys, foreign keys, unique keys and check rules."),
        ("REST API development", "Each blueprint has page routes (/admin/...) and JSON routes (/api/...). Create returns 201, update returns 200, a missing record returns 404, a rule conflict (for example converting an enquiry twice or paying more than the contract balance) returns 409, a missing permission returns 403 and a missing login returns 401. Lists are paginated and can be searched and filtered."),
        ("Authentication, validation, testing and deploying applications", "Passwords are stored as Werkzeug hashes. A successful login clears the old session, creates a new CSRF value and stores the user id, role and employee id in the signed session cookie. validators.py checks length, e-mail, phone, dates, money, choices and the submission token before any SQL runs. Six pytest tests run against a fresh SQLite file. The application is started by Gunicorn through wsgi.py."),
    ]:
        r.lead_with_body(f"{lead}:", body, num)
    r.h3("Data Analytics with Pandas and NumPy")
    num = r._new_num(13)
    for lead, body in [
        ("Loading data", "loader.py runs a SQL query and turns the result into a Pandas data frame, converting money columns to numbers. Each analytics module asks the loader for the table it needs and for the chosen date range, which comes from ranges.py (7 days, 30 days, 3 months, 6 months, this year or a custom range of up to ten years)."),
        ("Revenue from payment rows", "with_signed_amount() adds a signed_amount column using numpy.where: paid and partially paid keep the amount, refunded becomes negative and pending becomes zero. Total revenue, monthly revenue, revenue by service and period growth are all sums of this one column. The booking value is never counted as revenue."),
        ("Enquiry conversion", "Conversion rate = converted / eligible x 100. Eligible statuses are Contacted, Follow-up Required, Negotiation, Converted and Rejected; New is excluded because nobody has worked on it yet. The function _rate() returns None when there are no eligible enquiries, so the screen shows a dash instead of a false zero. The module also gives the monthly rate, the rate by event type and the average days from enquiry to conversion."),
        ("Customer, service, location and seasonal analysis", "Customer segments follow plain rules: high-value means lifetime collected spend at or above the 75th percentile (numpy.percentile), returning means two or more bookings, new means registered in the range with fewer than two bookings, one-time means exactly one booking and prospect means no booking. Service and location tables group bookings and revenue; seasonal demand groups bookings by the month of the event date and labels November to February as peak, March, April and October as moderate and May to September as lean."),
        ("Insights and the forecast guard", "insights.py turns the numbers into short sentences, for example the highest-revenue service or the change in conversion compared with the previous period of the same length. forecast.py fits a scikit-learn LinearRegression to the monthly series only when there are at least eight months of history and R squared is 0.15 or more; otherwise it returns a message that explains why no forecast is shown. Predicted values are never allowed to go below zero."),
    ]:
        r.lead_with_body(f"{lead}:", body, num)
    r.figure(f"{D}/13_status_lifecycles.png", "Status Lifecycles of Enquiries, Bookings, Projects and Payments", 6.0, 7.5)
    r.p(
        "Figure 4.5 shows the statuses stored in the database and how each one affects the numbers. Only New is left out of the conversion "
        "rate, and only Paid and Partially Paid add to revenue while Refunded subtracts from it."
    )
    r.h3("Cloud Deployment on Render")
    num = r._new_num(13)
    for lead, body in [
        ("Platform choice", "The first deployment attempt targeted a serverless platform, but an application that writes to a SQLite file and to a data folder needs a normal long-running process with a writable disk. Render runs the application as a web service from the GitHub repository, so it was selected. The free plan was used, so no money was spent on hosting."),
        ("Build and start", "render.yaml defines the service. The build command is pip install -r requirements.txt && python database/seed_data.py --reset, which installs the libraries and creates and fills the SQLite file. The start command is gunicorn -w 1 -b 0.0.0.0:$PORT wsgi:app. One worker is used because SQLite allows a single writer at a time."),
        ("Environment variables", "APP_ENV=production turns on the secure session cookie, PYTHON_VERSION is 3.12.8, SECRET_KEY is generated by Render, SQLITE_PATH points to instance/fotoinsight.db, and FIREBASE_DB_URL and FIREBASE_AUTH_TOKEN are left empty until the optional cloud copy is needed."),
        ("Health check and limits", "Render calls /health before it sends traffic to a new version. On the free plan the service sleeps after a period without requests, so the first request after a pause is slow, and the SQLite file is recreated by the build, so changes made on the live site are not permanent across deployments. These limits are listed again in Chapter 8."),
    ]:
        r.lead_with_body(f"{lead}:", body, num)
    r.figure(f"{D}/07_deployment_flow.png", "Deployment Flow of FotoInsight from GitHub to Render", 6.1)
    r.p(
        "Every push to the main branch of the GitHub repository starts a new build on Render. The build installs the libraries and seeds "
        "the SQLite database. Gunicorn then starts the Flask application, Render checks /health and the site becomes available over HTTPS. "
        "The optional Firebase Realtime Database is reached only when the admin presses the sync button."
    )
    r.table_caption("Major Engineering and Deployment Blockers Resolved During the Internship")
    r.table(
        ["Area", "Issue Observed", "Root Cause", "Implemented Fix"],
        [
            ["Database", "The project needed a MySQL server, which a free host does not provide.", "MySQL is a separate service and has to be installed, paid for or hosted elsewhere.", "Switched to SQLite and kept the MySQL-style SQL working through normalize_sql() in app/db.py."],
            ["Revenue", "Revenue looked too high when a booking had only an advance.", "The booking contract value was being treated as money received.", "Revenue is now the sum of payment rows with signs (paid and partially paid add, refunded subtracts, pending ignored). Covered by a pytest test."],
            ["Enquiry form", "A double click created two enquiries.", "Every submit was treated as a new record.", "One-time submission_token stored with a UNIQUE rule. A repeat returns the same reference code with duplicate set to true."],
            ["Forms", "A wrong field on the contact or enquiry form showed a raw JSON error.", "The same route handled both browser forms and JSON calls.", "A browser form post now shows the page again with the message and status 400. The JSON route keeps returning JSON."],
            ["Forecast", "A forecast line was drawn for data that has no trend.", "A straight line was fitted without checking the fit.", "Forecast needs at least 8 months and R squared of 0.15 or more. Otherwise the page says the forecast is hidden and shows the R squared value."],
            ["Deployment", "The live site was empty after the first release.", "The build created the application but not the database file.", "The Render build command runs database/seed_data.py --reset so that the SQLite file exists before Gunicorn starts."],
            ["Hosting", "A serverless host was not suitable for a SQLite file and a data folder.", "Serverless functions have no persistent writable disk or long-running process.", "Moved to a Render web service started with Gunicorn."],
        ],
        [1300, 2400, 2600, 3324],
        size=22,
    )
    r.h3("DevOps")
    num = r._new_num(13)
    for lead, body in [
        ("Git and GitHub", f"The source code is kept in the repository https://github.com/Madhavballabhkakkar/FotoInsight, with a README, deployment guides (DEPLOY_RENDER.md, DEPLOY_FREE.md), requirements files and the pytest configuration."),
        ("Build pipeline", "Render rebuilds the service from the main branch. The build is the same two commands that are run on a laptop, so what works locally also works on the server."),
        ("Monitoring", "The /health route returns a small JSON status that Render checks. The Data Sync page can be used to read back the Firebase summary, and the Render log shows Gunicorn start-up and request lines."),
    ]:
        r.list_item(f"**{lead}:** {body}", num)
    r.h2("Testing and Validation Strategy")
    r.p(
        "I first tested each rule on its own and then the full flow. The pure calculations (signed revenue, conversion rate, percentile and "
        "forecast guard) were checked with small known inputs. For example, a contract of INR 100000 with INR 30000 paid, INR 70000 pending and "
        "INR 5000 refunded must show net revenue of INR 25000, not INR 100000."
    )
    r.p(
        "The six automated tests in tests/test_app.py use a fresh SQLite file for every test and the Flask test client. They cover login and "
        "locked pages, the public pages and the duplicate enquiry, customer, enquiry and booking create, read, update and delete including the "
        "second conversion returning 409, the payment and revenue rule, the service, project and employee limits, and the analytics and the "
        "PDF, Excel and CSV reports. All six tests pass in about two seconds."
    )
    r.p(
        "Security and error cases were then checked by hand against a copy of the seeded database: an API call without login returned 401, an "
        "admin page without login redirected to the login page, a login request without a CSRF token returned 400, a wrong password returned 401, "
        "an unknown address returned 404 and a request body of 3 MB returned 413. System tests on the live Render site were carried out after the "
        "deployment: the public pages, the login, the overview, the analytics screen, a report download and the data sync page."
    )
    r.p(
        "Functional testing during the internship was reviewed with my External Guide Mr. Ajay Raj Kushwah, and the report format with my "
        "Internal Guide Ms. Namrata Kashyap. The tools used for testing were pytest, the Flask test client, the Chrome browser with its developer "
        "tools (Network, Console and device toolbar) and the Render dashboard logs."
    )
    r.table_caption("Functional, Security and Deployment Test Case Summary")
    r.table(
        ["Test ID", "Module / Area", "Test Scenario and Input", "Expected Result", "Observed Result / Status"],
        [
            ["TC-01", "Authentication", "Open /admin/customers and /api/customers without login; then log in with a wrong and a correct password.", "Page redirects to login, API returns 401, wrong password returns 401, correct login returns 200, logout locks the API again.", "Pass (pytest test_login_logout_and_locked_pages)"],
            ["TC-02", "CSRF Protection", "POST to /api/auth/login without the X-CSRF-Token header.", "Request is rejected with HTTP 400 and a clear message.", "Pass (checked by hand, 400)"],
            ["TC-03", "Public Enquiry", "Submit the same enquiry twice with the same submission token.", "First call returns 201 and a new code, second returns 200 with duplicate true and the same code.", "Pass (pytest and manual check, code ENQ-00341 repeated)"],
            ["TC-04", "Validation", "Send an enquiry with the e-mail address bad.", "HTTP 400 with the message Enter a valid email address.", "Pass (checked by hand)"],
            ["TC-05", "Enquiry to Booking", "Convert a negotiation enquiry to a booking with total 100000, then convert it again.", "First returns 201, second returns 409 because the booking already exists.", "Pass (pytest test_customer_enquiry_booking_crud)"],
            ["TC-06", "Payments and Revenue", "Booking of 100000 with paid 30000, pending 70000, refunded 5000, then a paid payment of 90000.", "Net revenue is 25000, not 100000, and the 90000 payment returns 409.", "Pass (pytest test_payment_revenue_is_not_the_contract)"],
            ["TC-07", "Role Limits", "Employee tries to create a service and to change the photographer of a project; employee updates project status and notes.", "Create service returns 403, photographer change returns 403, status and notes update returns 200.", "Pass (pytest test_service_project_and_employee_limits)"],
            ["TC-08", "Analytics", "Request analytics for a date range with no data (1990), then add a booking and a payment of 10000 and read the dashboard.", "Empty range returns zero revenue with a Not enough data message; revenue card shows 10000.", "Pass (pytest test_analytics_and_reports)"],
            ["TC-09", "Reports", "Download revenue as PDF, customers as CSV and the annual report as Excel.", "PDF starts with %PDF, CSV contains the report title, Excel file is a valid zip (PK).", "Pass (pytest)"],
            ["TC-10", "Upload Limit", "Send a request body of 3 MB to a public JSON route.", "Server rejects it with HTTP 413 because the limit is 2 MB.", "Pass (checked by hand, 413)"],
            ["TC-11", "Error Pages", "Open an address that does not exist.", "A styled 404 page is returned, not a stack trace.", "Pass (checked by hand, 404)"],
            ["TC-12", "Deployment", "Open https://fotoinsight.onrender.com/health and the home page after a deployment.", "Both return HTTP 200 and the live pages load with data.", "Pass (live site verified)"],
        ],
        [800, 1300, 2700, 2500, 2324],
        size=20,
        header_size=22,
        center_cols=(0,),
    )

    # ------------------------------------------------------------------ 5 Technologies
    r.h1("Technologies Used")
    r.p(
        "This chapter outlines the software frameworks and version numbers, the hardware used during the internship, the main code "
        "of the project and the tools used. Version numbers are those installed in the project environment (pip list) or taken from "
        "the requirements and the template files."
    )
    r.h2("Software Platform")
    r.h3("a) Front-end")
    r.p(
        "The front end consists of Jinja2 templates rendered by Flask, styled with Bootstrap and the project's own CSS files, with "
        "JavaScript for forms and charts. There is no separate JavaScript build step, so there is nothing to compile before deployment."
    )
    r.table_caption("Front-end Technologies")
    r.table(
        ["Category", "Package", "Version"],
        [
            ["Languages and markup", "HTML5, CSS3, JavaScript (ES6), Jinja2 templates", "Not applicable"],
            ["UI framework", "Bootstrap (CSS and bundle JS, stored in static/vendor)", "5.3.3"],
            ["Charts", "Chart.js (stored in static/vendor)", "4.4.1"],
            ["Own scripts", "api.js, dashboard.js, analytics.js, public.js", "Project files"],
            ["Own styles", "public.css, admin.css", "Project files"],
            ["Browser used for testing", "Google Chrome", "Current"],
        ],
        [2600, 4600, 2424],
    )
    r.h3("b) Back-end")
    r.p(
        "The server is a modular Flask application with a plain SQL model layer and an analytics package. The libraries below are those "
        "listed in requirements.txt and installed in the project environment."
    )
    r.table_caption("Back-end Technologies")
    r.table(
        ["Category", "Package", "Version"],
        [
            ["Language", "Python (local environment)", "3.15.2"],
            ["Language on Render", "Python (PYTHON_VERSION in render.yaml)", "3.12.8"],
            ["Web framework", "Flask", "3.1.3 (requirement: >=3.0,<4)"],
            ["WSGI and security helpers", "Werkzeug (password hashing, routing)", "3.1.9"],
            ["Template engine", "Jinja2", "3.1.6"],
            ["Production server", "Gunicorn", "27.0.1 (requirement: >=22)"],
            ["Data analysis", "pandas", "3.1.1 (requirement: >=2.2)"],
            ["Numerical computing", "NumPy", "2.5.5 (requirement: >=1.26)"],
            ["Forecast", "scikit-learn (LinearRegression, r2_score)", "1.9.1 (requirement: >=1.4)"],
            ["PDF reports", "fpdf2", "2.9.0 (requirement: >=2.7)"],
            ["Excel files", "openpyxl", "3.1.5 (requirement: >=3.1)"],
            ["Configuration", "python-dotenv", "1.2.4"],
            ["Testing", "pytest", "9.2.0"],
            ["Database engine", "SQLite 3 (Python standard library sqlite3)", "Bundled with Python"],
        ],
        [2600, 4200, 2824],
    )
    r.h3("c) Database / Cloud Platform")
    r.p(
        "SQLite is the database that has been implemented. During the 45 days it ran as a single file (instance/fotoinsight.db) "
        "created from database/schema_sqlite.sql and filled with synthetic records by database/seed_data.py: 8 employees, 2 users, "
        "220 customers, 12 services, 8 packages, 340 enquiries, 40 enquiry notes, 170 bookings, 246 booking team rows, 265 payments, "
        "80 projects and 12 feedback records. The file needs no server, no account and no cost, which suits a student project and a free hosting plan."
    )
    r.p("The cloud services used are:")
    num = r._new_num(5)
    for lead, body in [
        ("Render", "Free web service that builds the application from GitHub, runs Gunicorn, checks /health and gives the public HTTPS address https://fotoinsight.onrender.com/."),
        ("GitHub", "Remote repository https://github.com/Madhavballabhkakkar/FotoInsight that triggers each Render build."),
        ("Firebase Realtime Database", "Optional cloud copy. The application sends the bundle with an HTTP PUT to fotoinsight.json and reads a summary back with HTTP GET through the REST API, using only the Python urllib module."),
        ("Local data folder", "The data directory that holds the JSON, CSV and Excel copies of the six main tables and one JSON bundle."),
    ]:
        r.list_item(f"**{lead}:** {body}", num)
    r.h2("Hardware Platform")
    r.table_caption("Hardware Platform Used for Development and Testing")
    r.table(
        ["Environment", "Component", "Specification"],
        [
            ["Local development machine (Apple MacBook Pro)", "Processor", "Apple M6, 12 cores (2 Super, 4 Performance and 6 Efficiency)"],
            ["", "Memory (RAM)", "16 GB unified memory"],
            ["", "Storage", "SSD of about 1 TB (926 GiB formatted)"],
            ["", "Operating system", "macOS 27.0"],
            ["", "Network", "Wi-Fi broadband connection"],
            ["Cloud service (Render free plan)", "Compute", "Free web service, 512 MB RAM, one Gunicorn worker"],
            ["", "Runtime", "Python 3.12.8 on Linux"],
            ["", "Storage", "Application disk recreated at each build; SQLite file stored inside the application folder"],
            ["End-user devices", "Clients", "Any desktop, laptop, tablet or mobile phone with a modern browser"],
        ],
        [2269, 1692, 5663],
    )
    r.h2("Code")
    r.p("The following extracts show the most important logic of the project. Each one is copied from the source code with only comments shortened.")
    r.h3("Snippet 1: Signed Revenue Column with NumPy")
    r.p(
        "Revenue is not read from the booking. This function adds one column in which paid and partially paid amounts keep their sign, "
        "refunded amounts become negative and pending amounts become zero. All revenue totals are sums of this column."
    )
    r.code("app/analytics/loader.py", "PYTHON", [
        "def with_signed_amount(frame):",
        "    if frame.empty:",
        "        return frame",
        "    status = frame[\"status\"].astype(str).to_numpy()",
        "    amount = frame[\"amount\"].to_numpy(dtype=float)",
        "    signed = np.where(",
        "        np.isin(status, [\"paid\", \"partially_paid\"]),",
        "        amount,",
        "        np.where(status == \"refunded\", -amount,",
        "                 np.zeros(len(amount), dtype=float)),",
        "    )",
        "    out = frame.copy()",
        "    out[\"signed_amount\"] = signed",
        "    return out",
    ])
    r.h3("Snippet 2: Conversion Rate with a Safe Division")
    r.p(
        "The rate is converted divided by eligible times 100. If nothing is eligible the function returns None so that the screen can "
        "show that there is no rate, instead of showing a misleading zero. The eligible statuses are kept in one constant."
    )
    r.code("app/analytics/enquiry_analysis.py and app/constants.py", "PYTHON", [
        "ELIGIBLE_ENQUIRY_STATUSES = (\"contacted\", \"follow_up\",",
        "                             \"negotiation\", \"converted\", \"rejected\")",
        "",
        "def _rate(converted, eligible):",
        "    if eligible <= 0:",
        "        return None",
        "    return round(float(np.divide(converted, eligible) * 100.0), 1)",
    ])
    r.h3("Snippet 3: Forecast Guard")
    r.p(
        "A straight-line forecast is calculated only when at least eight months of history exist. After fitting, the R squared value "
        "is checked, and a weak fit hides the numbers and explains why."
    )
    r.code("app/analytics/forecast.py", "PYTHON", [
        "MINIMUM_MONTHS = 8",
        "",
        "if values.size < MINIMUM_MONTHS or float(np.sum(values)) <= 0:",
        "    return {\"available\": False, \"name\": name, ...}",
        "model = LinearRegression()",
        "model.fit(x_values, values)",
        "fitted = model.predict(x_values)",
        "score = float(r2_score(values, fitted))",
        "if score < 0.15:",
        "    return {\"available\": False, \"name\": name,",
        "            \"message\": f\"... (R\u00b2 {score:.2f}). Forecast numbers are hidden ...\"}",
        "future_x = np.arange(len(values), len(values) + 3,",
        "                     dtype=float).reshape(-1, 1)",
        "predicted = np.maximum(model.predict(future_x), 0)",
    ])
    r.h3("Snippet 4: CSRF Check for Every Change Request")
    r.p(
        "Before any POST, PUT, PATCH or DELETE reaches a route, the token sent by the browser must match the token stored in the session. "
        "API and fetch calls get a JSON error and normal forms get an error page."
    )
    r.code("app/__init__.py", "PYTHON", [
        "@app.before_request",
        "def check_csrf():",
        "    if request.method not in (\"POST\", \"PUT\", \"PATCH\", \"DELETE\"):",
        "        return None",
        "    sent = request.headers.get(\"X-CSRF-Token\", \"\")",
        "    if not sent:",
        "        payload = request.get_json(silent=True) or {}",
        "        sent = payload.get(\"csrf_token\") or request.form.get(\"csrf_token\") or \"\"",
        "    if sent != session.get(\"csrf\"):",
        "        message = \"Invalid or missing security token. Refresh the page and try again.\"",
        "        if request.path.startswith(\"/api/\") or request.is_json:",
        "            return jsonify({\"error\": message}), 400",
        "        return render_template(\"error.html\", message=message), 400",
    ])
    r.h3("Snippet 5: Role Decorator and Employee Scope")
    r.p(
        "admin_required blocks a signed-in employee with HTTP 403. employee_scope returns the employee id for an employee and None for "
        "an admin, so that the same query can add a filter only for employees."
    )
    r.code("app/authz.py", "PYTHON", [
        "def employee_scope():",
        "    if session.get(\"role\") == \"employee\":",
        "        return session.get(\"employee_id\")",
        "    return None",
        "",
        "def admin_required(view):",
        "    @wraps(view)",
        "    def wrapper(*args, **kwargs):",
        "        if \"user_id\" not in session:",
        "            ... # 401 for API calls, redirect to login for pages",
        "        if session.get(\"role\") != \"admin\":",
        "            ... # 403 JSON or an error page",
        "        return view(*args, **kwargs)",
        "    return wrapper",
    ])
    r.h3("Snippet 6: MySQL-Style SQL Normalised for SQLite")
    r.p(
        "The queries use %s placeholders and a few MySQL date functions. This function rewrites them just before they run on SQLite, "
        "so that the model code did not need to be rewritten when the database was changed."
    )
    r.code("app/db.py", "PYTHON", [
        "def normalize_sql(sql: str) -> str:",
        "    out = sql.replace(\"%s\", \"?\")",
        "    out = re.sub(r\"\\bCURDATE\\(\\)\", \"date('now')\", out, flags=re.I)",
        "    out = re.sub(r\"DATE_FORMAT\\(([^,]+),\\s*'%Y-%m'\\)\",",
        "                 r\"strftime('%Y-%m', \\1)\", out, flags=re.I)",
        "    out = re.sub(r\"\\bYEAR\\(([^)]+)\\)\",",
        "                 r\"CAST(strftime('%Y', \\1) AS INTEGER)\", out, flags=re.I)",
        "    return out",
    ])
    r.h3("Snippet 7: Render Blueprint")
    r.p("This file tells Render how to build, start and check the application.")
    r.code("render.yaml", "YAML", [
        "services:",
        "  - type: web",
        "    name: fotoinsight",
        "    runtime: python",
        "    plan: free",
        "    buildCommand: pip install -r requirements.txt && python database/seed_data.py --reset",
        "    startCommand: gunicorn -w 1 -b 0.0.0.0:$PORT \"wsgi:app\"",
        "    healthCheckPath: /health",
        "    envVars:",
        "      - key: APP_ENV",
        "        value: production",
        "      - key: PYTHON_VERSION",
        "        value: \"3.12.8\"",
        "      - key: SECRET_KEY",
        "        generateValue: true",
        "      - key: SQLITE_PATH",
        "        value: instance/fotoinsight.db",
    ])
    r.h2("Tools")
    r.table_caption("Tools Used During the Internship")
    r.table(
        ["Tool Name", "Vendor", "Version", "Purpose in Project"],
        [
            ["Cursor (code editor)", "Anysphere", "Current release", "Main code editor for the Python, template, JavaScript and configuration files"],
            ["Python and pip", "Python Software Foundation", "3.15.2 (local), 3.12.8 (Render)", "Language runtime and package installation in a virtual environment"],
            ["Git", "Software Freedom Conservancy", "2.54.0 (Apple Git-157)", "Version control and pushing to GitHub"],
            ["GitHub", "GitHub, Inc.", "Web service", "Remote repository and trigger for Render builds"],
            ["Render", "Render Services, Inc.", "Free web service plan", "Cloud hosting, Gunicorn start, /health check and logs"],
            ["pytest", "pytest-dev", "9.2.0", "Six automated tests with the Flask test client"],
            ["Google Chrome with DevTools", "Google LLC", "Current", "Network, Console and device checks of the live pages and screenshots"],
            ["sqlite3 module", "Python Software Foundation / SQLite Consortium", "Bundled with Python", "Inspecting tables, keys and row counts of the SQLite file"],
            ["Firebase Realtime Database", "Google LLC", "REST API", "Optional cloud copy of the exported bundle"],
            ["Microsoft Word", "Microsoft Corporation", "Current", "Preparing and formatting this report"],
        ],
        [2100, 2000, 2000, 3524],
        size=22,
    )

    # ------------------------------------------------------------------ 6 Results
    r.h1("Results and Discussion")
    r.p(
        "The FotoInsight photography studio website and analytics dashboard was built for Fotographiya Ventures Pvt. Ltd. to bring the "
        "public website, the studio records and the business numbers into one application. All the objectives set at the start of the "
        "internship were achieved. The application is live at https://fotoinsight.onrender.com/ and the source code is in the GitHub "
        "repository https://github.com/Madhavballabhkakkar/FotoInsight."
    )
    r.p(
        "The production setup uses a Render free web service with Gunicorn, a SQLite database file created and seeded during the build, "
        "and the optional Firebase Realtime Database copy. Every number below comes from the synthetic demonstration data. The live "
        "application states this on every staff screen so that nobody mistakes it for the real performance of the studio."
    )
    r.h2("Principal Screens and Features")
    r.p(
        "For the public website, the system offers the following screens (Annexure E): the Home page with the studio name, tagline and "
        "featured services; the About page with the introduction, mission and vision read from the settings table; the Services page "
        "with each service and its packages and prices; the Portfolio page; the Contact page that saves a message as an enquiry; and the "
        "Enquiry form that asks for name, e-mail, phone, event type, date, location, city, guest count, package, budget and requirements, "
        "and shows the reference code after submission."
    )
    r.p(
        "The protected staff area begins with a login page at /admin/login. After signing in, the Overview page shows eight KPI cards "
        "(total customers, total enquiries, confirmed bookings, total revenue, pending enquiries, upcoming events, completed projects and "
        "conversion rate), three insight sentences and charts of monthly revenue and monthly bookings. With the range set to This year "
        "(01 January 2026 to 23 November 2026), the live demonstration showed 220 customers, 81 enquiries, 31 confirmed bookings, total "
        "collected revenue of INR 19,91,860.15, 132 pending enquiries, 26 upcoming events, 18 completed projects and a conversion rate of 53.4 percent."
    )
    r.p(
        "The Customers, Enquiries, Bookings, Services, Projects and Payments pages have search boxes, filters and pagination. The Payments "
        "page shows net revenue, collected amount before refunds, refunds and the outstanding amount on active contracts, so that the owner "
        "can see at once that revenue is not the same as the contract value. The Analytics page explains how each number is defined and then shows "
        "the business insights, revenue, customers, enquiry conversion, service performance, seasonal demand and forecast sections. "
        "The Reports page downloads six reports, the Data Sync page writes the local copies and talks to Firebase, and the Settings page "
        "edits the business details, employees and employee logins."
    )
    r.h2("Test Results and Production Verification")
    r.p(
        "Test cases TC-01 to TC-12, as mentioned in section 4.2, were tested on the local application and on the live Render site. All "
        "six automated tests passed, and the manual security checks gave the expected status codes: 401 for an API call without login, "
        "400 for a missing CSRF token, 401 for a wrong password, 404 for an unknown address and 413 for a body larger than 2 MB."
    )
    r.p(
        "The money rule was verified with a known case: a contract of INR 100000 with INR 30000 paid, INR 70000 pending and INR 5000 refunded "
        "gave net revenue of INR 25000, and a further payment of INR 90000 was refused with HTTP 409. On the live site, the Payments page "
        "showed net revenue of INR 1,22,04,607.36, which equals collected payments of INR 1,23,15,865.71 minus refunds of INR 1,11,258.35, "
        "with INR 25,16,427.94 still outstanding on active contracts and pending rows of INR 37,254.32 left out of revenue."
    )
    r.p(
        "The enquiry conversion section for the same live range showed 81 enquiries in total, 73 eligible after excluding 8 new ones, 39 "
        "converted and a rate of 53.4 percent, with an average of 8.1 days to convert. The insight text also reported that the conversion "
        "rate fell from 61.1 percent to 53.4 percent compared with the previous period of the same length. The customer section showed "
        "220 customers by the end of the period, 44 new, 6 returning in the range and an average spend of INR 46,601. Customer segments were "
        "37 high-value (lifetime collected spend of INR 1,12,059 or more), 15 returning, 42 new, 108 one-time and 65 prospects."
    )
    r.p(
        "The forecast guard worked as designed. The live Analytics page said that there were 46 months of booking history and 47 months of "
        "collected revenue history, but a straight line did not describe them (R squared 0.00 and 0.01), so the forecast numbers were hidden. "
        "This is the correct result for the synthetic data, which has no real trend."
    )
    r.h2("Performance Observations")
    r.p(
        "Response times were measured in the project environment with the Flask test client against a copy of the seeded SQLite database "
        "(220 customers, 340 enquiries, 170 bookings and 265 payments), taking the median of 10 requests. This measures the application "
        "itself and does not include internet delay or the start-up delay of the free Render plan."
    )
    r.table_caption("Median Response Time of Main Routes (milliseconds)")
    r.table(
        ["Route", "Type", "Median time (ms)", "HTTP status"],
        [
            ["/ (home page)", "Public HTML page", "0.9", "200"],
            ["/services", "Public HTML page", "0.6", "200"],
            ["/health", "Health check", "0.3", "200"],
            ["/api/customers", "JSON list (paginated)", "0.9", "200"],
            ["/api/enquiries", "JSON list (paginated)", "0.6", "200"],
            ["/api/payments", "JSON list with summary", "0.8", "200"],
            ["/api/dashboard", "KPI cards and charts", "36.5", "200"],
            ["/api/analytics (this year)", "Full analytics with Pandas and forecast", "38.5", "200"],
            ["/api/reports/revenue (CSV)", "Report download", "4.7", "200"],
        ],
        [3400, 3000, 1824, 1400],
        center_cols=(2, 3),
    )
    r.p(
        "The two heaviest routes, the dashboard and the full analytics, both finish in under 40 milliseconds because Pandas works on a few "
        "hundred rows. The only slow moment a visitor can notice is the first request after the free Render service has been idle, when the "
        "service must wake up; this depends on the hosting plan and not on the code."
    )
    r.h2("Discussion: Evaluation Against Internship Objectives")
    r.table_caption("Evaluation of Delivered Outcomes Against the Objectives of Section 1.3")
    r.table(
        ["Objective from Section 1.3", "Delivered Outcome", "Status"],
        [
            ["1. Public website and private staff dashboard with Flask and SQLite", "Six public pages and thirteen staff blueprints with search, filters and pagination, built on Jinja2 and Bootstrap, live on Render", "Achieved"],
            ["2. 13-table database and duplicate-safe enquiry form", "Schema with keys, unique rules and checks; seeded with 220 customers and 340 enquiries; submission token returns the same code on a repeat", "Achieved"],
            ["3. Correct analytics with Pandas and NumPy", "Revenue from signed payment rows, conversion with New excluded, customer segments, service, location and seasonal tables, insight sentences and a guarded forecast", "Achieved"],
            ["4. Practical application security", "Password hashing, session cookie, CSRF check on every change, admin and employee roles with scope, validation, 2 MB limit and error pages", "Achieved"],
            ["5. Testing, deployment and data export", "Six pytest tests passing, Render deployment with a health check, six reports in three formats, local JSON, CSV and Excel copies and Firebase REST sync", "Achieved (Firebase needs the owner's database address)"],
            ["6. Full life cycle in 45 days", "Seven stages from requirement analysis to maintenance, with weekly plan and handover", "Achieved"],
        ],
        [3000, 4824, 1800],
    )
    r.p(
        "Two lessons stand out from these findings. First, a number on a dashboard is only useful when its rule is written next to it and "
        "is the same in the code, the screen and the report. Writing the definitions of revenue and conversion before coding saved a lot of "
        "rework. Second, a good analytics tool must know when to say nothing. Hiding a forecast that does not fit the data, and showing a dash "
        "when no enquiry is eligible, make the system more trustworthy than showing a confident but wrong number."
    )
