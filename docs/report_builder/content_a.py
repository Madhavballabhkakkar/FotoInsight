"""Chapters 1 to 3."""

TITLE = "FotoInsight: Photography Studio Website and Data Analytics Dashboard"
LIVE = "https://fotoinsight.onrender.com/"
REPO = "https://github.com/Madhavballabhkakkar/FotoInsight"
D = "docs/report_assets/diagrams"


def build(r, A):
    # ------------------------------------------------------------------ 1 Introduction
    r.h1("Introduction")
    r.p(
        "This section describes my internship journey as a **Data Analyst (Intern)** at **Fotographiya Ventures Pvt. Ltd.**, Kota, "
        "for 45 days from 01st June 2026 to 15th July 2026. During this period I built and deployed **FotoInsight**, a photography "
        "studio website with a staff dashboard and a Pandas and NumPy analytics section, using Flask, SQLite and Chart.js. "
        "The Background, Problem Statement, Objectives and Scope of Work of the project are discussed in this chapter."
    )
    r.h2("Background")
    r.p(
        "This project relates to the wedding and event photography business. Fotographiya Ventures Pvt. Ltd., based in Kota, Rajasthan "
        "(https://www.fotographiya.com/), provides wedding photography, pre-wedding shoots, destination weddings, corporate events, "
        "birthday parties, roka ceremonies and portfolio shoots. A studio like this handles many small pieces of information every day: "
        "who asked about a date, who was called back, which booking is confirmed, how much advance was paid, who is shooting and who is editing."
    )
    r.p(
        "In many small studios these records live in phone contacts, chat messages and paper notes. The owner can see the work, "
        "but not the pattern. It is hard to say which service brings the most money, which month is busy, how many enquiries "
        "actually become bookings, or how much money is still to be collected. Answering these questions by hand takes hours "
        "and the answers are often guesses."
    )
    r.p(
        "A web application that keeps customers, enquiries, bookings, payments and projects in one database solves the first half "
        "of the problem. The second half is analysis: the stored records must be turned into numbers that are correct and "
        "explained in plain words. For this reason the project combines a conventional Flask web application with an "
        "analytics layer written with Pandas and NumPy, so that the studio website and the studio data analysis live in one system."
    )
    r.p(
        "A free, zero-configuration database was chosen so that the project can run on a student laptop and on a free cloud plan. "
        "SQLite stores the data in a single file, and the same code can also write a local JSON, CSV and Excel copy and a Firebase "
        "Realtime Database copy. The application is hosted on Render and is available at https://fotoinsight.onrender.com/."
    )
    r.h2("Problem Statement")
    r.p(
        "The studio needs a public website that attracts clients and records every enquiry, and a private area where the team can "
        "manage the work and read reliable business numbers. The existing way of working has the following problems."
    )
    r.h3("Records and Workflow")
    r.p(
        "Enquiries arrive through calls, messages and forms, and there is no single list that shows their status. A client who "
        "submits a form twice may be counted twice. When an enquiry becomes a booking, the link between the two is not stored, "
        "so the studio cannot say how long the conversion took. Payments are noted separately from bookings, so the amount "
        "still to be collected has to be calculated by hand. Employees can see all information even when they only need their own jobs."
    )
    r.h3("Analysis and Trust in Numbers")
    r.p(
        "Revenue is often confused with the booking value. A booking of INR 100000 with an advance of INR 30000 has not yet "
        "produced INR 100000 of revenue. In the same way, a conversion rate that counts brand-new enquiries as failures looks "
        "lower than the truth. Charts that look impressive but use unclear rules mislead the owner. Predictions that are shown "
        "even when the history is too short or too irregular are worse than no prediction."
    )
    r.h3("Solution")
    r.p(
        "FotoInsight is a Flask web application with a public studio website and a login-protected staff dashboard. Every enquiry "
        "form carries a one-time submission token, so a repeated submit returns the same reference code instead of a new record. "
        "A database of 13 tables links customers, enquiries, bookings, team members, payments, projects and feedback. "
        "Revenue is calculated only from payment rows (paid and partially paid add, refunded subtracts, pending is ignored), and "
        "conversion is calculated as converted enquiries divided by eligible enquiries, where the status New is excluded. "
        "Pandas reads the tables into data frames and NumPy performs the calculations. A straight-line forecast made with "
        "scikit-learn is shown only when there are at least eight months of history and the fit is good enough (R squared of 0.15 or more); "
        "otherwise the page says that the forecast is hidden and why. Employees see only the work assigned to them, "
        "and every change request must carry a CSRF token."
    )
    r.h2("Objectives of the Internship / Study")
    r.p("My objectives within this internship were:")
    r.numbered(
        [
            "Designing and building a public photography studio website and a private staff dashboard for Fotographiya Ventures Pvt. Ltd. using Flask, SQLite, Jinja2 templates and Bootstrap.",
            "Designing a relational database of 13 tables that connects customers, enquiries, bookings, payments, projects and team members, together with a reliable enquiry form that blocks duplicate submissions.",
            "Implementing correct business analytics with Pandas and NumPy: revenue from payment rows, enquiry conversion rate, customer segments, service performance, seasonal demand and a guarded forecast, each shown with a plain-language explanation.",
            "Implementing practical application security: password hashing, session login, CSRF tokens, admin and employee roles, input validation and safe error pages.",
            "Hands-on experience in testing, deployment and data export: automated tests with pytest, deployment on Render with a health check, PDF, Excel and CSV reports, local JSON, CSV and Excel copies and a Firebase Realtime Database copy.",
            "Following a complete software development life cycle during this internship (01/06/2026 to 15/07/2026): requirement analysis, design, coding, integration, testing, deployment and handover.",
        ]
    )
    r.h2("Scope of the Work")
    r.p(
        "Within the 45-day project timeline (01 June 2026 to 15 July 2026), a photography studio website with a staff dashboard and an "
        "analytics section was developed with Flask and SQLite at Fotographiya Ventures Pvt. Ltd. in Kota, and later deployed on Render. "
        "The application can be found here: https://fotoinsight.onrender.com/. The records shown in the application are synthetic "
        "demonstration records created by the seed script; the application displays a notice on every staff screen to say that "
        "these numbers are not the real business performance of Fotographiya or any other studio."
    )
    r.h3("User Types")
    r.p("The application has three kinds of users:")
    r.numbered(
        [
            ("Public Visitor", "Unauthenticated person using a mobile or desktop browser. The visitor can read the studio pages, see services and the portfolio, send a contact message and submit an event enquiry."),
            ("Studio Employee", "A staff member with a personal login linked to an employee record. An employee can see the overview, view customers, enquiries, bookings and projects assigned to him or her, add enquiry notes and update the status and notes of own projects. Services, payments, analytics, reports, data sync and settings are closed to employees."),
            ("Studio Admin", "A seeded administrator. The admin can create, edit and delete all records, assign enquiries, convert an enquiry to a booking, record payments, read analytics, download reports, export and sync data, and manage services, packages, settings and employee logins."),
        ]
    )
    r.h3("In-Scope Functionalities")
    r.bullets(
        [
            ("Public website", "Home, About, Services, Portfolio, Contact and Enquiry pages rendered with Jinja2 and styled with Bootstrap 5.3.3. Business details, services and packages come from the database. Enquiry and contact forms carry a submission token and return a reference code."),
            ("Staff dashboard", "Overview with eight KPI cards, a date-range filter, Chart.js charts and a global search. Customers, enquiries, bookings, services, projects and payments pages with search, filters and pagination."),
            ("Analytics with Pandas and NumPy", "Revenue, enquiry conversion, customer segments, service performance, location and seasonal demand tables, plain-language insights and a guarded straight-line forecast made with scikit-learn."),
            ("Security", "Werkzeug password hashing, signed session cookie (HttpOnly, SameSite Lax, 8 hours), CSRF token on every change request, admin and employee roles, server-side validation of every field, 2 MB upload limit and custom error pages."),
            ("Reports and data copies", "Six reports in PDF, Excel and CSV, a local data folder with JSON, CSV and Excel copies of the six main tables, and a Firebase Realtime Database copy through its REST API."),
            ("Testing and deployment", "Six automated pytest tests, a /health endpoint, a Render blueprint (render.yaml) and a build step that creates and seeds the SQLite database."),
        ]
    )
    r.h3("Out of scope")
    r.bullets(
        [
            ("Public sign-up and client login", "Clients cannot create accounts or see their own bookings online. Only the studio team signs in."),
            ("Online payment gateway", "Payments are recorded by staff after money is received. No card, UPI or bank gateway is connected, and no invoices are generated."),
            ("Real studio data", "All numbers in this project are synthetic demonstration data. Importing the real records of the studio was not part of the internship."),
            ("Custom domain, mobile app and e-mail or SMS alerts", "The site uses the default Render address. There is no native mobile application and no automatic notification to customers."),
            ("Machine-learning prediction beyond a straight line", "Only a simple linear trend is offered, and it is hidden when the history is short or the fit is weak."),
        ]
    )

    # ------------------------------------------------------------------ 2 Organization
    r.h1("Internship / Organization Overview")
    r.p(
        "In this chapter I have described the organisation where I did my internship of 45 days as a Data Analyst. I have also "
        "described the tasks and responsibilities that I had to perform during my internship period."
    )
    r.h2("About the Organization")
    r.p(
        "Fotographiya Ventures Pvt. Ltd (https://www.fotographiya.com/) is a private limited startup providing photography and video "
        "services for various events including weddings. It is located in F-3 Ballabh Bari, Near 7 Wonders, Electricity Board Area, "
        "Kota, Rajasthan (Pin: 324007). A brief description about the company is provided in the section 'Brief About the Company' at "
        "the beginning of this report. Hence, only the key points are presented here."
    )
    r.p(
        "The company provides photography for weddings, pre-wedding sessions, destination weddings, corporate events, birthday and "
        "roka events and portfolio sessions. Website and media platforms are also maintained to make it easy for customers to learn "
        "about the services. The company is managed by Mr. Mohit Barthunia (Founder and CEO) and Ms. Princu Kherada (Director). "
        "My technical mentor during the internship was Mr. Ajay Raj Kushwah (External Guide)."
    )
    r.h2("Duration and Mode of the Internship")
    r.p(
        "The project was conducted for a duration of 45 days (01 June 2026 to 15 July 2026) following a structured software development "
        "life cycle in seven stages, with the coding done in five build phases. This internship was a part of BCA Colloquium-II "
        "(CAC771) of Career Point University, Kota. I was regularly monitored by my External Guide Mr. Ajay Raj Kushwah and Internal "
        "Guide Ms. Namrata Kashyap. Once the main application was developed and delivered, it was deployed on the Render cloud "
        "platform to make it available on the internet."
    )
    r.table_caption("Internship Duration and Mode")
    r.table(
        ["Particular", "Details"],
        [
            ["Start Date", "01 June 2026"],
            ["End Date", "15 July 2026"],
            ["Total Duration", "45 Days"],
            ["Mode of Internship", "Hybrid"],
            ["Designation", "Data Analyst (Intern)"],
            ["Organisation", "Fotographiya Ventures Pvt. Ltd., Kota, Rajasthan"],
        ],
        [3200, 6424],
    )
    r.h2("Role and Responsibilities During the Internship")
    r.p(
        "My designation was Data Analyst (Intern). I worked on the whole studio website and analytics project, from understanding "
        "the studio workflow to deployment, and my main responsibilities and deliverables were:"
    )
    r.numbered(
        [
            ("Requirement analysis and data design", "Studied how an enquiry becomes a booking, a payment and a delivered project. Listed the data that the studio must track. Wrote the definitions of revenue and conversion rate before writing any code. Designed the 13-table SQLite schema with primary keys, foreign keys, unique keys and check constraints."),
            ("Backend, authentication and security", "Built the Flask application factory, 13 route blueprints, plain-SQL model layer, validators and error handlers. Implemented login with hashed passwords, session cookies, CSRF checks, admin and employee roles and the employee scope filter."),
            ("Frontend and dashboard", "Built the public pages and the staff screens with Jinja2 and Bootstrap, and the overview and analytics charts with Chart.js. Wrote the small fetch helper (api.js) that sends the CSRF token with every change request."),
            ("Analytics, reports and data copies", "Wrote the Pandas loader, the signed revenue column, conversion, customer segment, service, location and seasonal calculations and the insight sentences. Added the guarded forecast, the PDF, Excel and CSV reports, the local JSON, CSV and Excel store and the Firebase REST sync."),
            ("Testing, deployment and handover", "Wrote six pytest tests, checked security rules by hand, measured response times and deployed the application on Render with a health check. Prepared the user notes and handed the source code and report over."),
        ]
    )
    r.p("At the end of the internship, I delivered the working application along with the handover documentation.")

    # ------------------------------------------------------------------ 3 Project description
    r.h1("Project Description")
    r.p(
        "The FotoInsight studio website and analytics dashboard is the application I built during the internship and later deployed on "
        "Render. This chapter gives a breakdown of each module. It also includes an overview of the data flow, the system architecture "
        "(Flask, SQLite and Pandas on Render), the skills developed and the weekly plan over the course of 45 days."
    )
    r.h2("Project Modules")
    mods = [
        ("Public Studio Website Module:", "Six public pages: Home, About, Services, Portfolio, Contact and Enquiry. Business name, address, social links and mission text are read from the business_settings table. Active services and their packages are listed from the database. The enquiry form checks every field on the server and returns a reference code such as ENQ-00341. A contact message is saved in the same enquiries table with the source set to contact, so that nothing is lost. The pages are responsive and use the vendored Bootstrap 5.3.3 files, so they work without a content delivery network."),
        ("Customer, Enquiry and Booking Management Module:", "Customers can be created, searched, edited and deleted (a customer with bookings cannot be deleted because of the RESTRICT rule). Enquiries have six statuses, notes, an assigned employee and a one-click conversion to a booking. A booking stores the event, the amount, the status and the team (lead photographer, photographer, cinematographer, editor, assistant, coordinator). Conversion is allowed only once: the second attempt returns HTTP 409."),
        ("Payments and Project Tracking Module:", "Payment rows belong to a booking and carry the amount, date, method (UPI, cash, bank transfer, card, other), reference and status (paid, pending, partially paid, refunded). A payment that would exceed the contract balance is rejected with HTTP 409. Each booking can have one project that moves from Not Started through In Progress, Editing and Review to Completed and Delivered, with a photographer and an editor assigned."),
        ("Analytics and Insights Module:", "The app/analytics package has eleven small modules: loader, ranges, overview, revenue, enquiry_analysis, customer_analysis, service_analysis, location, seasonal, forecast and insights. Pandas reads the SQL results into frames and NumPy calculates the totals, percentages, percentiles and trend. Each chart is accompanied by its definition and a sentence in plain English."),
        ("Reports, Export and Cloud Copy Module:", "Admin can download six reports (monthly revenue, booking, customer, enquiry conversion, service performance and annual business report) as PDF (fpdf2), Excel (openpyxl) or CSV. The Data Sync page writes the six main tables (customers, enquiries, bookings, payments, services and projects) to JSON, CSV and Excel files under the data folder and can send a bundle of all tables to a Firebase Realtime Database over REST and read back a summary."),
        ("Security, Roles and Settings Module:", "Login with hashed passwords, CSRF-protected change requests, admin_required and login_required decorators, employee_scope filters, a settings page for business details, employee records and employee logins, and a password change page for every signed-in user."),
    ]
    num_id = r._new_num(18)
    for lead, body in mods:
        r.lead_with_body(lead, body, num_id)

    r.h2("Context Diagram (High Level)")
    r.figure(f"{D}/01_context_diagram.png", "Level-0 Context Diagram of the FotoInsight Studio Platform", 6.1)
    r.p(
        "The context diagram shows the whole application as one process (0.0). Everything outside the process is an external entity, "
        "and every arrow is a data flow that crosses the boundary of the system."
    )
    r.bullets(
        [
            ("Entities", "Visitor or Client, Studio Employee, Studio Admin, Firebase Realtime Database, the Local Data Folder and the Render web service that hosts and health-checks the application."),
            ("Inputs", "Page requests, enquiry and contact forms, login details, status and note updates, records and payments entered by the admin, the chosen date range, report requests, sync requests and health-check requests."),
            ("Functionality", "Page rendering, validation, login and role checks, record keeping, analytics with Pandas and NumPy, report building, local export and cloud copy."),
            ("Outputs", "Web pages, the enquiry reference code, KPI cards, charts, insight sentences, a forecast or a hidden-forecast message, PDF, Excel and CSV files, JSON, CSV and Excel exports and a health status."),
        ]
    )
    r.h2("System Architecture / Data Flow Overview")
    r.figure(f"{D}/02_system_architecture.png", "System Architecture and Data Flow Overview of FotoInsight on Render", 6.2)
    r.h3("Public:")
    r.p(
        "A visitor opens the Render address in a browser. Gunicorn passes the request to the Flask application. The public blueprint "
        "reads the business settings, services and packages from SQLite, fills a Jinja2 template and returns plain HTML styled with Bootstrap. "
        "When the visitor submits the enquiry form, the browser sends the fields together with a submission token. The server validates "
        "each field, looks for the same token in the enquiries table, and either returns the existing reference code (duplicate) or creates "
        "the customer link and a new enquiry row and returns a new code with HTTP 201."
    )
    r.h3("Admin and Employee (Read/Write):")
    r.p(
        "On the login page the browser sends the username, password and CSRF token. After the password hash is verified, the server opens "
        "a signed session cookie that holds the user id, role and employee id. A before_request hook then checks every later request: "
        "a missing session returns 401 for API calls or redirects to the login page, a wrong role returns 403, and every POST, PUT, PATCH or "
        "DELETE must carry the X-CSRF-Token header. The model layer sends plain SQL to SQLite (one connection per request). "
        "For analytics, the loader runs the SQL, Pandas builds data frames and NumPy produces the numbers that the JSON API returns to Chart.js."
    )
    r.h2("Internship Training Details and Learning Outcomes")
    r.bullets(
        [
            ("Languages and web development", "Python 3, HTML5, CSS3, JavaScript (ES6), SQL, Jinja2 templates, Bootstrap 5, the fetch API and Chart.js 4 for charts."),
            ("Backend development and security", "Flask application factory, blueprints, before_request hooks, error handlers, Werkzeug password hashing, signed sessions, CSRF tokens, role decorators, validation of every input and safe JSON errors."),
            ("Databases", "Relational design with 13 tables, primary and foreign keys, unique and check constraints, ON DELETE rules, indexes, a MySQL-style SQL normaliser for SQLite, and seeding of synthetic data."),
            ("Data analysis with Pandas and NumPy", "Reading SQL into data frames, grouping by month, signed amounts with numpy.where, percentiles, safe division, period-on-period growth, and clear definitions that match the screen text."),
            ("Reporting, deployment and DevOps", "fpdf2 and openpyxl reports, JSON, CSV and Excel exports, Firebase REST calls with urllib, pytest, Git and GitHub, Gunicorn, Render blueprint and health check."),
        ]
    )
    r.h2("Week-wise Training Activities")
    r.table_caption("Week-wise Training Activities and Learning Outcomes")
    r.table(
        ["Week No.", "Duration / Dates", "Training Activities / Topics Covered", "Learning Outcome"],
        [
            ["Week 1", "01 June 2026 to 07 June 2026 (Days 1 to 7)", "Study of the studio workflow from enquiry to delivery, list of the data to track, written definitions of revenue and conversion rate, choice of Flask, SQLite and Pandas, first draft of the 13-table schema and the route list.", "Learned to plan a data system before coding and to agree on metric definitions first."],
            ["Week 2", "08 June 2026 to 14 June 2026 (Days 8 to 14)", "Final schema in schema_sqlite.sql with keys and check rules, app factory, config and database layer, seed script with synthetic records, base templates and the public Home, About, Services, Portfolio and Contact pages.", "Learned relational design, constraints and how to seed realistic test data."],
            ["Week 3", "15 June 2026 to 21 June 2026 (Days 15 to 21)", "Enquiry form with submission token, contact form, login and logout, session cookie, CSRF hook, admin and employee roles, admin layout, customers and enquiries pages, notes.", "Learned secure session login, CSRF protection and duplicate-safe form handling."],
            ["Week 4", "22 June 2026 to 28 June 2026 (Days 22 to 28)", "Bookings and booking team, enquiry-to-booking conversion with 409 on repeat, payments with balance check, projects with photographer and editor, employee_scope limits, global search.", "Learned to model money and workflow rules and to return correct HTTP status codes."],
            ["Week 5", "29 June 2026 to 05 July 2026 (Days 29 to 35)", "Pandas loader, signed revenue column, conversion rate, customer segments, service, location and seasonal tables, insight sentences, overview and analytics screens with Chart.js.", "Learned to calculate business metrics with Pandas and NumPy and to explain them in words."],
            ["Week 6", "06 July 2026 to 12 July 2026 (Days 36 to 42)", "Forecast guard with scikit-learn, six reports in PDF, Excel and CSV, local JSON, CSV and Excel store, Firebase REST sync, integration of all modules, six pytest tests and manual security checks.", "Learned to guard weak predictions, to export data and to test the full flow."],
            ["Week 7", "13 July 2026 to 15 July 2026 (Days 43 to 45)", "Bug fixes, response-time checks, interface polish, screenshots, written documentation and handover of the source code and report.", "Learned to finish, document and hand over a project."],
            ["Cloud Deployment Phase", "After handover", "Deployment on Render using render.yaml (build command seeds SQLite, start command runs Gunicorn, /health check), environment variables, optional Firebase settings and live testing at https://fotoinsight.onrender.com/.", "Learned production configuration, health checks and free-plan limits."],
        ],
        [1403, 1701, 3969, 2551],
        center_cols=(0,),
    )
