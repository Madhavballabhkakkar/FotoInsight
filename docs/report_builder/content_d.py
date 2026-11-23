"""Annexure D (data dictionary) and Annexure E (screenshots)."""

C = "docs/report_assets/compressed"

TS = "Timestamp text (YYYY-MM-DD HH:MM:SS) set by SQLite when the row is created; no later change."
TS_UP = "Timestamp text refreshed whenever the row is edited."
DEMO = "Flag: 1 marks synthetic demonstration rows created by the seed script; 0 for rows entered by staff or visitors."

TABLES = [
    (
        "Table D.1: Employees Table (employees)",
        "Studio staff who can be assigned to enquiries, bookings and projects.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier of the staff member."),
            ("full_name", "TEXT", "Full name of the staff member; required."),
            ("email", "TEXT", "Work e-mail address; required."),
            ("phone", "TEXT", "Contact phone number; required."),
            ("job_title", "TEXT", "Role in the studio, for example photographer, cinematographer or editor."),
            ("city", "TEXT", "City where the staff member is based."),
            ("status", "TEXT", "Employment state, default active."),
            ("is_demo", "INTEGER", DEMO),
            ("created_at", "TEXT", TS),
            ("updated_at", "TEXT", TS_UP),
        ],
    ),
    (
        "Table D.2: Users Table (users)",
        "Login accounts for the staff area.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier of the login account."),
            ("username", "TEXT", "[UK] Unique login name; required."),
            ("email", "TEXT", "[UK] Unique e-mail address of the account."),
            ("password_hash", "TEXT", "Werkzeug password hash; the plain password is never stored."),
            ("role", "TEXT", "Access role of the account: admin or employee."),
            ("employee_id", "INTEGER", "[FK] employees.id. Staff member behind the login; empty for the admin account; ON DELETE SET NULL."),
            ("display_name", "TEXT", "Name shown in the top bar."),
            ("is_active", "INTEGER", "1 when the account may sign in, 0 when it is disabled; default 1."),
            ("created_at", "TEXT", TS),
            ("updated_at", "TEXT", TS_UP),
        ],
    ),
    (
        "Table D.3: Customers Table (customers)",
        "People and families who enquire about or book the studio.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier; shown as CUS-00001 style codes in the screens."),
            ("full_name", "TEXT", "Full name of the customer; required."),
            ("email", "TEXT", "E-mail address; required."),
            ("phone", "TEXT", "Phone number; required."),
            ("city", "TEXT", "City of the customer; used in the city filter and the location analysis."),
            ("address", "TEXT", "Optional postal address."),
            ("registration_date", "TEXT", "Date (YYYY-MM-DD) on which the customer was registered; used for new customer counts."),
            ("is_demo", "INTEGER", DEMO),
            ("created_at", "TEXT", TS),
            ("updated_at", "TEXT", TS_UP),
        ],
    ),
    (
        "Table D.4: Services Table (services)",
        "Services offered by the studio and shown on the public Services page.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier of the service."),
            ("name", "TEXT", "[UK] Unique service name, for example Wedding Photography."),
            ("slug", "TEXT", "[UK] Unique URL-friendly name."),
            ("category", "TEXT", "Group of the service, used for the filter chips on the Portfolio page."),
            ("description", "TEXT", "Short description shown to visitors."),
            ("image_path", "TEXT", "Optional path of the image shown with the service."),
            ("base_price", "REAL", "Starting price in INR; CHECK base_price >= 0."),
            ("status", "TEXT", "active or inactive; only active services appear on the public site."),
            ("sort_order", "INTEGER", "Display order on the Services page; default 0."),
            ("is_demo", "INTEGER", DEMO),
            ("created_at", "TEXT", TS),
            ("updated_at", "TEXT", TS_UP),
        ],
    ),
    (
        "Table D.5: Packages Table (packages)",
        "Priced packages that belong to a service.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier of the package."),
            ("service_id", "INTEGER", "[FK] services.id. Service that the package belongs to; ON DELETE RESTRICT."),
            ("name", "TEXT", "Package name, for example Basic Wedding Package."),
            ("description", "TEXT", "Optional explanation of the package."),
            ("price", "REAL", "Package price in INR; CHECK price >= 0."),
            ("inclusions", "TEXT", "Optional list of what is included, for example hours and team size."),
            ("status", "TEXT", "active or inactive; default active."),
            ("is_demo", "INTEGER", DEMO),
            ("created_at", "TEXT", TS),
            ("updated_at", "TEXT", TS_UP),
        ],
    ),
    (
        "Table D.6: Enquiries Table (enquiries)",
        "Enquiries received from the website, the contact form or entered by staff.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier of the enquiry."),
            ("enquiry_code", "TEXT", "[UK] Reference code shown to the visitor and in the lists, for example ENQ-00341."),
            ("customer_id", "INTEGER", "[FK] customers.id. Customer linked to the enquiry; may be empty; ON DELETE RESTRICT."),
            ("full_name", "TEXT", "Name given in the form; required."),
            ("email", "TEXT", "E-mail given in the form; required."),
            ("phone", "TEXT", "Phone number given in the form; required."),
            ("event_type", "TEXT", "Service or event type chosen by the visitor."),
            ("event_date", "TEXT", "Planned event date (YYYY-MM-DD); optional."),
            ("event_location", "TEXT", "Venue or place of the event; optional."),
            ("city", "TEXT", "City of the event; optional."),
            ("guest_count", "INTEGER", "Expected number of guests; optional."),
            ("package_id", "INTEGER", "[FK] packages.id. Preferred package; optional; ON DELETE SET NULL."),
            ("estimated_budget", "REAL", "Budget in INR given by the visitor; optional."),
            ("requirements", "TEXT", "Free text with additional requirements."),
            ("status", "TEXT", "Workflow status: new, contacted, follow_up, negotiation, converted or rejected; default new."),
            ("assigned_employee_id", "INTEGER", "[FK] employees.id. Staff member who follows up; ON DELETE SET NULL."),
            ("submission_token", "TEXT", "[UK] Random token created by the browser form; a repeated token returns the existing enquiry instead of creating a new one."),
            ("source", "TEXT", "Where the enquiry came from: website, contact or admin; default website."),
            ("is_demo", "INTEGER", DEMO),
            ("created_at", "TEXT", TS),
            ("updated_at", "TEXT", TS_UP),
        ],
    ),
    (
        "Table D.7: Enquiry Notes Table (enquiry_notes)",
        "Follow-up notes written by staff on an enquiry.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier of the note."),
            ("enquiry_id", "INTEGER", "[FK] enquiries.id. Enquiry that the note belongs to; ON DELETE CASCADE."),
            ("user_id", "INTEGER", "[FK] users.id. Login that wrote the note; ON DELETE RESTRICT."),
            ("note", "TEXT", "Text of the note; required."),
            ("created_at", "TEXT", TS),
        ],
    ),
    (
        "Table D.8: Bookings Table (bookings)",
        "Confirmed jobs, created directly or by converting an enquiry.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier of the booking."),
            ("booking_code", "TEXT", "[UK] Reference code, for example BKG-00163."),
            ("customer_id", "INTEGER", "[FK] customers.id. Customer who booked; ON DELETE RESTRICT."),
            ("enquiry_id", "INTEGER", "[UK][FK] enquiries.id. Enquiry that was converted; unique, so an enquiry converts only once; ON DELETE RESTRICT."),
            ("service_id", "INTEGER", "[FK] services.id. Booked service; ON DELETE RESTRICT."),
            ("package_id", "INTEGER", "[FK] packages.id. Booked package; optional; ON DELETE SET NULL."),
            ("event_name", "TEXT", "Name of the event shown in the lists."),
            ("event_type", "TEXT", "Type of the event."),
            ("event_date", "TEXT", "Date of the event (YYYY-MM-DD); used by the calendar and the seasonal analysis."),
            ("event_location", "TEXT", "Venue of the event."),
            ("city", "TEXT", "City of the event; used by the location analysis."),
            ("total_amount", "REAL", "Contract value in INR; CHECK total_amount > 0. It is not revenue by itself."),
            ("status", "TEXT", "confirmed, in_progress, completed, cancelled or on_hold; default confirmed."),
            ("notes", "TEXT", "Optional internal notes."),
            ("is_demo", "INTEGER", DEMO),
            ("created_at", "TEXT", TS),
            ("updated_at", "TEXT", TS_UP),
        ],
    ),
    (
        "Table D.9: Booking Team Table (booking_team)",
        "Staff assigned to a booking with a role.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier of the assignment."),
            ("booking_id", "INTEGER", "[FK] bookings.id. Booking being staffed; ON DELETE CASCADE."),
            ("employee_id", "INTEGER", "[FK] employees.id. Assigned staff member; ON DELETE RESTRICT."),
            ("team_role", "TEXT", "Role on this booking: Lead Photographer, Photographer, Cinematographer, Editor, Assistant or Coordinator."),
            ("is_lead", "INTEGER", "1 for the lead of the booking, otherwise 0."),
            ("created_at", "TEXT", TS),
            ("(booking_id, employee_id, team_role)", "UNIQUE", "[UK] The same person cannot be given the same role twice on one booking."),
        ],
    ),
    (
        "Table D.10: Payments Table (payments)",
        "Money recorded against a booking. All revenue figures are calculated from this table.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier of the payment."),
            ("payment_code", "TEXT", "[UK] Reference code, for example PAY-154-pai-546."),
            ("booking_id", "INTEGER", "[FK] bookings.id. Booking that the payment belongs to; ON DELETE CASCADE."),
            ("amount", "REAL", "Amount in INR; CHECK amount > 0. The sign is decided by the status."),
            ("payment_date", "TEXT", "Date of the payment (YYYY-MM-DD); revenue by month uses this date."),
            ("method", "TEXT", "upi, cash, bank_transfer, card or other."),
            ("transaction_ref", "TEXT", "Optional bank or UPI reference."),
            ("status", "TEXT", "paid, pending, partially_paid or refunded; default paid. Paid and partially paid add to revenue, refunded subtracts, pending is ignored."),
            ("notes", "TEXT", "Optional notes."),
            ("recorded_by", "INTEGER", "[FK] users.id. Login that recorded the payment; ON DELETE SET NULL."),
            ("is_demo", "INTEGER", DEMO),
            ("created_at", "TEXT", TS),
            ("updated_at", "TEXT", TS_UP),
        ],
    ),
    (
        "Table D.11: Projects Table (projects)",
        "Delivery work (shoot, editing, handover) for a booking.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier of the project."),
            ("project_code", "TEXT", "[UK] Reference code, for example PRJ-00066."),
            ("booking_id", "INTEGER", "[UK][FK] bookings.id. Booking that the project delivers; unique, so there is one project per booking; ON DELETE CASCADE."),
            ("photographer_id", "INTEGER", "[FK] employees.id. Photographer in charge; ON DELETE SET NULL."),
            ("editor_id", "INTEGER", "[FK] employees.id. Editor in charge; ON DELETE SET NULL."),
            ("start_date", "TEXT", "Planned start date; optional."),
            ("delivery_date", "TEXT", "Promised delivery date; a project is delayed when this date has passed and it is not finished."),
            ("status", "TEXT", "not_started, in_progress, editing, review, completed or delivered; default not_started."),
            ("notes", "TEXT", "Progress notes; employees may edit this field and the status."),
            ("is_demo", "INTEGER", DEMO),
            ("created_at", "TEXT", TS),
            ("updated_at", "TEXT", TS_UP),
        ],
    ),
    (
        "Table D.12: Customer Feedback Table (customer_feedback)",
        "Ratings and comments given by customers.",
        [
            ("id", "INTEGER", "[PK] Auto-increment identifier of the feedback."),
            ("customer_id", "INTEGER", "[FK] customers.id. Customer who gave the feedback; ON DELETE CASCADE."),
            ("booking_id", "INTEGER", "[FK] bookings.id. Related booking; optional; ON DELETE SET NULL."),
            ("rating", "INTEGER", "Rating from 1 to 5; CHECK rating BETWEEN 1 AND 5."),
            ("comment", "TEXT", "Text of the comment."),
            ("is_public", "INTEGER", "1 when the comment may be shown on the public site; default 0."),
            ("is_demo", "INTEGER", DEMO),
            ("created_at", "TEXT", TS),
        ],
    ),
    (
        "Table D.13: Business Settings Table (business_settings)",
        "Studio details used on the public pages. The table always holds exactly one row.",
        [
            ("id", "INTEGER", "[PK] Always 1; CHECK id = 1 keeps exactly one settings row."),
            ("business_name", "TEXT", "Studio name shown in the header and footer."),
            ("tagline", "TEXT", "Short line shown under the name."),
            ("email", "TEXT", "Public contact e-mail."),
            ("phone", "TEXT", "Public contact phone."),
            ("address", "TEXT", "Studio address shown on the Contact page."),
            ("city", "TEXT", "Studio city."),
            ("map_lat", "REAL", "Latitude of the studio for the map."),
            ("map_lng", "REAL", "Longitude of the studio for the map."),
            ("instagram_url", "TEXT", "Optional Instagram link."),
            ("facebook_url", "TEXT", "Optional Facebook link."),
            ("youtube_url", "TEXT", "Optional YouTube link."),
            ("about_intro", "TEXT", "Introduction paragraph of the About page."),
            ("mission", "TEXT", "Mission statement shown on the About page."),
            ("vision", "TEXT", "Vision statement shown on the About page."),
            ("updated_at", "TEXT", TS_UP),
        ],
    ),
]


def build_d(r, A):
    r.annex("D", "Data Dictionary (DD)")
    r.p(
        "The field-level definitions of the 13 tables of the SQLite database (database/schema_sqlite.sql) are outlined in this annexure. "
        "The definitions follow the entity-relationship diagram presented in Annexure B. Most business tables carry the housekeeping columns "
        "is_demo, created_at and updated_at. SQLite stores dates and times as text, money as REAL and flags as INTEGER 0 or 1."
    )
    r.p("In the description column, PK means Primary Key, UK means Unique Key and FK means Foreign Key.")
    for caption, _intro, rows in TABLES:
        r.table_caption(caption.split(": ", 1)[1])
        r.table(
            ["Fields", "Data Type", "Description"],
            [[a, b, c] for a, b, c in rows],
            [2200, 1300, 6124],
            size=20,
            header_size=22,
            bold_first=False,
        )


SHOTS = [
    # (heading, description, image, caption, width_in)
    ("Home Page - Studio Landing View:", "Landing view of the public site at the home page, with the top navigation (About, Services, Portfolio, Contact, ADMIN), the headline and the three buttons Explore our work, View services and Submit an enquiry.", "01_home.jpg", "Public home page of the live FotoInsight site hosted on Render"),
    ("About Page:", "About page with the mission, vision, what the studio covers and how a job is run. The number of services mentioned in the text is read from the database.", "02_about.jpg", "About page with mission, vision and the way a job is run"),
    ("Services Page:", "Services with their starting prices and packages, each with an Enquire button. The prices come from the services and packages tables and are edited from the staff dashboard.", "03_services.jpg", "Services page with starting prices, packages and the Enquire button"),
    ("Portfolio Page:", "Image gallery with filter chips for All work, Wedding, Pre-wedding, Destination, Corporate, Engagement, Birthday, Cinematography and Albums. The images are royalty-free demonstration photographs.", "04_portfolio.jpg", "Portfolio gallery with category filters"),
    ("Contact Page:", "Studio contact details from the settings table and the contact form with name, e-mail, phone and message. A sent message is stored as an enquiry with the source contact.", "05_contact.jpg", "Contact page with studio details and message form"),
    ("Event Enquiry Form:", "Enquiry form with name, e-mail, phone, event type, date, location, city, number of guests, preferred package, estimated budget and requirements. A submission token prevents duplicates and the visitor receives a reference code.", "12_enquiry_form.jpg", "Event enquiry form of the public site"),
    ("Studio Login:", "Sign-in screen of the staff area at /admin/login with username and password. Administrators manage the whole studio and employees see only the work assigned to them.", "06_login.jpg", "Studio login page"),
    ("Overview Dashboard - KPI Cards and Insights:", "Overview with eight KPI cards (total customers, total enquiries, confirmed bookings, total revenue, pending enquiries, upcoming events, completed projects and conversion rate), each with its definition, followed by three generated insight sentences and the date-range selector.", "15_overview.jpg", "Overview dashboard with KPI cards, definitions and insight sentences"),
    ("Customers:", "Customer list with search, city filter and sort, showing the customer code, contact details, city, registration date, number of bookings and spending, which is collected money and not the contract value.", "13_customers.jpg", "Customer list with filters, bookings and collected spending"),
    ("Enquiries:", "Enquiry list with search, event type, status and date filters. Each row shows the reference code, name, event, date, status badge and assigned employee.", "16_enquiries.jpg", "Enquiry list with filters, status badges and assigned employee"),
    ("Bookings:", "Booking list with code, customer, event, date, contract value, collected amount, amount left and status. The Calendar and Create booking buttons are at the top.", "14_bookings.jpg", "Booking list with contract, collected and outstanding amounts"),
    ("Payments:", "Payments page, available to the admin, with the revenue rule at the top and four summary cards: net revenue, collected before refunds, refunds and outstanding on active contracts. The table lists each payment with method and status.", "17_payments.jpg", "Payments page with net revenue, refunds and outstanding amount"),
    ("Projects:", "Project list with project code, event, customer, photographer, editor, delivery date and status. Delayed projects are marked beside the delivery date and can be filtered with the Delayed only button.", "18_projects.jpg", "Project list with team, delivery date and delayed marker"),
    ("Reports:", "Six downloadable reports (Monthly Revenue, Booking, Customer, Enquiry Conversion, Service Performance and Annual Business) with a date range and a PDF, Excel or CSV format selector.", "19_reports.jpg", "Reports page with six reports and format selector"),
    ("Settings:", "Business information form that feeds the public pages (name, tagline, e-mail, phone, address, city and map position). The page also lists the employees who can be assigned to jobs.", "20_settings.jpg", "Settings page with business information"),
    ("Data Sync:", "Local storage and cloud synchronisation page with the buttons Export to local files, Push to Firebase and Read from Firebase, and the list of files in the data folder. The first paragraph in this screenshot still says MySQL; the wording in the source code was later corrected to SQLite, which is the database that the application uses.", "10_data_sync.jpg", "Data Sync page with local export and Firebase REST buttons"),
    ("Analytics - Definitions and Business Insights:", "Top of the Analytics page: How the numbers are defined, followed by the generated business insights for the selected date range. The sentence that names the source of the figures also said MySQL in this screenshot; it was corrected to SQLite in the source code afterwards.", "21_analytics_insights.jpg", "Analytics page with definitions and business insights"),
    ("Analytics - Revenue:", "Revenue section with collected, refunds, pending (excluded) and average booking value, a monthly collected revenue line and revenue by service.", "23_analytics_revenue.jpg", "Revenue analytics with monthly line chart and revenue by service"),
    ("Analytics - Customers:", "Customer section with customers by period end, new in range, returning and average spend, the segment rule table (high-value, returning, new, one-time, prospect) and the high-value list.", "24_analytics_customers.jpg", "Customer analytics with segments and high-value customers"),
    ("Analytics - Enquiry Conversion:", "Conversion section showing total enquiries, eligible enquiries, converted enquiries and the rate, with the note that New enquiries are excluded and the average days to convert.", "25_analytics_conversion.jpg", "Enquiry conversion analytics for the selected range"),
    ("Analytics - Service Performance:", "Service table with enquiries, bookings, collected amount and average contract, plus a one-line summary of the most enquired, least enquired, highest revenue and most booked services.", "26_analytics_service.jpg", "Service performance table"),
    ("Analytics - Seasonal Demand:", "Seasonal demand by the labelled wedding-season rule, the monthly heat strip and the weekday chart, counted by event date.", "27_analytics_seasonal.jpg", "Seasonal demand with season table, month strip and weekday chart"),
    ("Analytics - Forecast Guard:", "The forecast card. Because a straight line did not describe the 46 months of booking history (R squared 0.00) or the 47 months of revenue history (R squared 0.01), the numbers are hidden and the reason is shown.", "28_analytics_forecast.jpg", "Forecast section with the hidden-forecast message"),
]


def build_e(r, A):
    r.annex("E", "Screen Shots")
    r.p(
        "The screens below were captured from the live application at https://fotoinsight.onrender.com/ using the seeded demonstration "
        "data. Public pages are shown first, followed by the staff area (admin view) and the analytics sections."
    )
    for i, (head, desc, img, cap) in enumerate(SHOTS):
        r.h3(head)
        r.p(desc)
        r.figure(f"{C}/{img}", cap, 5.8, 4.2)
        if i % 2 == 1:
            r.page_break()
