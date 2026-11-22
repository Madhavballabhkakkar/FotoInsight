# FotoInsight

FotoInsight is a photography business website and office system for a final-year project. Visitors can browse services and send an enquiry. Staff can manage customers, bookings, payments, and projects, then study the business with Pandas, NumPy, and Chart.js.

The sample studio is called FotoInsight Studio. Every customer, enquiry, booking, payment, and project created by the seed script is **synthetic demo data**. It is not Fotographiya's real performance, and it is not any other studio's accounts. The admin screens say this on a banner.

## Demo logins

After you load the sample data:

| Who | Username | Password | What they can do |
| --- | --- | --- | --- |
| Administrator | `admin` | `Admin@123` | The whole office, including money, analytics, and reports |
| Employee | `employee` | `Employee@123` | Assigned enquiries, customers, and bookings, plus project status |

Change these passwords from **Settings** before you put the app on a public server. They are for a local demonstration.

## Run it on your computer

No MySQL server is required. The app uses a SQLite file.

1. Install Python 3.

2. In this folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

3. Edit `.env` and set `SECRET_KEY` to a long random string. Do not commit `.env`.

4. Build the tables and the demo rows (this recreates `instance/fotoinsight.db`):

```bash
python database/seed_data.py --reset
python run.py
```

5. Open [http://127.0.0.1:5000](http://127.0.0.1:5000) (or port `5050` if you set `PORT=5050`). The office is at `/admin/login`.

Free deploy notes: see `DEPLOY_RENDER.md` and `DEPLOY_FREE.md`.

## How to test each part

Automated checks (they use `fotoinsight_test`, not your demo data):

```bash
pytest -q
```

By hand:

| What you want to check | What to do |
| --- | --- |
| Public site | Open Home, About, Services, Portfolio, Enquiry, and Contact. Prices should match **Services** in the office. |
| Enquiry | Submit the form. You should see a code such as `ENQ-00341`. Refreshing and sending the same form token does not create a second row. |
| Login | Wrong password is rejected. Logging out sends you back to the login page. `/admin` without a login redirects. |
| Customers | Search, filter by city, add, edit, open a customer, read booking history. Spending is collected money, not the contract. |
| Enquiries | Filter by status and event. Assign someone. Add a note. **Convert to booking** once. A second click is refused. |
| Bookings | Switch between the table and the calendar. Collected and remaining are calculated from payments. |
| Payments | Record an advance as Paid. The revenue cards must not jump by the full contract. A Pending row is listed but not added to revenue. A Refunded row reduces revenue. |
| Projects | Create one from a booking. Mark a delivery date in the past and leave the status as Editing: it shows as delayed. Sign in as `employee` and change only the status. |
| Analytics | Change **This year** to **Last 30 days**. Charts and sentences change. The conversion sentence on the page states which statuses are included. |
| Reports | Download a PDF, an Excel file, and a CSV. Each file names the date range and says the rows are demo data. |
| Empty range | In analytics, choose a custom range in 1990. You should see zeros and a sentence that there is not enough data, not a made-up chart. |

## Where the important logic lives

- Tables: `database/schema.sql`
- Demo rows: `database/seed_data.py`
- Form checks: `app/validators.py`
- SQL for each screen: `app/models/`
- Maths: `app/analytics/` (`revenue.py`, `customer_analysis.py`, `enquiry_analysis.py`, `service_analysis.py`, `seasonal.py`, `location.py`, `insights.py`, `forecast.py`)
- Downloads: `app/reports/generators.py`
- Pages: `app/templates/`

The design notes, the diagram, and the module list are in [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Rules the numbers follow

**Revenue.** Add payments with status Paid or Partially Paid. Subtract Refunded. Ignore Pending. Never treat the booking total as money received just because an advance was taken.

**Conversion.** `converted ÷ eligible × 100`. Eligible means Contacted, Follow-up Required, Negotiation, Converted, and Rejected. New enquiries are counted in the total, but not in the ratio, because they have not been worked.

**Segments.** High-value means lifetime collected spend at or above the 75th percentile, and only after at least four paying customers exist. Returning means two or more bookings. A prospect has no booking.

**Forecast.** A straight line is fit with scikit-learn only when there are at least eight months of history and the line actually fits (R² of 0.15 or better). Otherwise the page says a forecast is not shown. Predicted points are labeled as predictions.

**Seasons.** November to February is treated as peak wedding season, March, April, and October as moderate, and May to September as lean. That is a labeled rule for this demo.

## Deploying it

Local development uses `python run.py`.

For a server:

1. Set `APP_ENV=production` and a real `SECRET_KEY` in the server environment. Production turns on secure session cookies, so the site should be served over HTTPS.
2. Point `MYSQL_*` at the production database. Do not reuse the demo password.
3. Run `python database/seed_data.py --reset` only on an empty demo database. Do not point `--reset` at a database you need to keep.
4. Serve the app with a production WSGI server and let Nginx (or similar) serve `app/static`:

```bash
APP_ENV=production gunicorn -w 2 -b 127.0.0.1:8000 "run:app"
```

`/health` returns `{"ok": true, "database": "up"}` when MySQL answers.

## Technology

HTML, CSS, JavaScript, Bootstrap 5, Chart.js, Python, Flask, Jinja, MySQL, Pandas, NumPy, scikit-learn (forecast only), fpdf2, and openpyxl. No React, Node, or MongoDB.
