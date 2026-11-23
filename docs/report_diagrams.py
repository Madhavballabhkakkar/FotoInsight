"""Black-and-grey diagrams for the FotoInsight internship report.

Run:  .venv/bin/python docs/report_diagrams.py
Writes PNG files to docs/report_assets/diagrams/.  Only PIL is used.
"""

import math
import os

from PIL import Image, ImageDraw, ImageFont

OUT = os.path.join(os.path.dirname(__file__), "report_assets", "diagrams")
os.makedirs(OUT, exist_ok=True)

REG = "/System/Library/Fonts/Supplemental/Arial.ttf"
BLD = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
MONO = "/System/Library/Fonts/Supplemental/Courier New.ttf"

K = (0, 0, 0)
W = (255, 255, 255)
G1 = (244, 244, 244)
G2 = (225, 225, 225)
G3 = (200, 200, 200)
G4 = (120, 120, 120)


def font(size, bold=False, mono=False):
    return ImageFont.truetype(MONO if mono else (BLD if bold else REG), size)


class Canvas:
    def __init__(self, width, height):
        self.w, self.h = width, height
        self.im = Image.new("RGB", (width, height), W)
        self.d = ImageDraw.Draw(self.im)

    # ---------- text ----------
    def wrap(self, text, fnt, maxw):
        lines = []
        for para in str(text).split("\n"):
            words = para.split(" ")
            cur = ""
            for word in words:
                trial = (cur + " " + word).strip()
                if self.d.textlength(trial, font=fnt) <= maxw or not cur:
                    cur = trial
                else:
                    lines.append(cur)
                    cur = word
            lines.append(cur)
        return lines

    def text(self, cx, cy, text, size=32, bold=False, maxw=None, fill=K, gap=6, anchor="c", mono=False):
        fnt = font(size, bold, mono)
        lines = self.wrap(text, fnt, maxw) if maxw else str(text).split("\n")
        lh = size + gap
        total = lh * len(lines) - gap
        y = cy - total / 2 if anchor in ("c", "l") else cy
        for line in lines:
            tw = self.d.textlength(line, font=fnt)
            x = cx - tw / 2 if anchor == "c" else cx
            self.d.text((x, y), line, font=fnt, fill=fill)
            y += lh
        return total

    # ---------- shapes ----------
    def box(self, x0, y0, x1, y1, text="", size=32, bold=False, fill=W, width=3, radius=0, pad=14, dash=False, align="c"):
        if radius:
            self.d.rounded_rectangle((x0, y0, x1, y1), radius=radius, fill=fill, outline=K, width=width)
        else:
            self.d.rectangle((x0, y0, x1, y1), fill=fill, outline=K, width=width)
        if text:
            if align == "c":
                self.text((x0 + x1) / 2, (y0 + y1) / 2, text, size, bold, maxw=(x1 - x0) - 2 * pad)
            else:
                self.text(x0 + pad, y0 + pad, text, size, bold, maxw=(x1 - x0) - 2 * pad, anchor="tl")

    def ellipse(self, x0, y0, x1, y1, text="", size=32, bold=False, fill=W, width=3):
        self.d.ellipse((x0, y0, x1, y1), fill=fill, outline=K, width=width)
        if text:
            self.text((x0 + x1) / 2, (y0 + y1) / 2, text, size, bold, maxw=(x1 - x0) * 0.78)

    def store(self, x0, y0, x1, y1, ident, text, size=30):
        self.d.rectangle((x0, y0, x1, y1), fill=G1, outline=None)
        self.d.line((x0, y0, x1, y0), fill=K, width=3)
        self.d.line((x0, y1, x1, y1), fill=K, width=3)
        idw = 78
        self.d.line((x0 + idw, y0, x0 + idw, y1), fill=K, width=3)
        self.d.line((x0, y0, x0, y1), fill=K, width=3)
        self.text(x0 + idw / 2, (y0 + y1) / 2, ident, size, True)
        self.text((x0 + idw + x1) / 2, (y0 + y1) / 2, text, size, False, maxw=(x1 - x0 - idw) - 24)

    def line(self, pts, width=3, dash=False, fill=K):
        for a, b in zip(pts[:-1], pts[1:]):
            if dash:
                self._dash(a, b, width, fill)
            else:
                self.d.line((a[0], a[1], b[0], b[1]), fill=fill, width=width)

    def _dash(self, a, b, width, fill, on=18, off=12):
        dx, dy = b[0] - a[0], b[1] - a[1]
        length = math.hypot(dx, dy)
        if length == 0:
            return
        ux, uy = dx / length, dy / length
        pos = 0.0
        while pos < length:
            end = min(pos + on, length)
            self.d.line((a[0] + ux * pos, a[1] + uy * pos, a[0] + ux * end, a[1] + uy * end), fill=fill, width=width)
            pos += on + off

    def head(self, tip, frm, size=22):
        dx, dy = tip[0] - frm[0], tip[1] - frm[1]
        length = math.hypot(dx, dy) or 1
        ux, uy = dx / length, dy / length
        px, py = -uy, ux
        base = (tip[0] - ux * size, tip[1] - uy * size)
        pts = [tip, (base[0] + px * size * 0.42, base[1] + py * size * 0.42), (base[0] - px * size * 0.42, base[1] - py * size * 0.42)]
        self.d.polygon(pts, fill=K)

    def arrow(self, pts, label=None, lp=None, lsize=26, lmax=300, dash=False, both=False, width=3):
        shaft = list(pts)
        self.line(shaft, width, dash)
        self.head(shaft[-1], shaft[-2])
        if both:
            self.head(shaft[0], shaft[1])
        if label:
            if lp is None:
                best, bi = 0, 0
                for i in range(len(shaft) - 1):
                    seg = math.hypot(shaft[i + 1][0] - shaft[i][0], shaft[i + 1][1] - shaft[i][1])
                    if seg > best:
                        best, bi = seg, i
                lp = ((shaft[bi][0] + shaft[bi + 1][0]) / 2, (shaft[bi][1] + shaft[bi + 1][1]) / 2)
            self.tag(lp[0], lp[1], label, lsize, lmax)

    def tag(self, cx, cy, label, size=26, maxw=300):
        fnt = font(size)
        lines = self.wrap(label, fnt, maxw)
        lh = size + 4
        tw = max(self.d.textlength(line, font=fnt) for line in lines)
        th = lh * len(lines)
        self.d.rectangle((cx - tw / 2 - 8, cy - th / 2 - 4, cx + tw / 2 + 8, cy + th / 2 + 2), fill=W)
        y = cy - th / 2
        for line in lines:
            lw = self.d.textlength(line, font=fnt)
            self.d.text((cx - lw / 2, y), line, font=fnt, fill=K)
            y += lh

    def title(self, text, y=36, size=40):
        self.text(self.w / 2, y, text, size, True)

    def save(self, name):
        path = os.path.join(OUT, name)
        self.im.save(path, optimize=True)
        print("saved", path, self.im.size)


def ell_point(cx, cy, rx, ry, tx, ty):
    dx, dy = tx - cx, ty - cy
    if dx == 0 and dy == 0:
        return cx, cy
    t = 1 / math.sqrt((dx / rx) ** 2 + (dy / ry) ** 2)
    return cx + dx * t, cy + dy * t


def offset_pair(a, b, delta):
    dx, dy = b[0] - a[0], b[1] - a[1]
    length = math.hypot(dx, dy) or 1
    px, py = -dy / length * delta, dx / length * delta
    return (a[0] + px, a[1] + py), (b[0] + px, b[1] + py)


# =====================================================================
# 1. Context diagram (level 0)
# =====================================================================
def context():
    c = Canvas(1800, 1240)
    px0, px1 = 650, 1150
    c.d.rounded_rectangle((px0, 40, px1, 1200), radius=60, fill=G2, outline=K, width=5)
    c.text((px0 + px1) / 2, 620, "0.0\nFotoInsight Studio Platform\n\nFlask web application\nSQLite database\nPandas and NumPy analytics\nCharts, reports and sync", 36, True, maxw=440)
    ents = [
        ("L", 190, "Visitor / Client", ("Page requests, enquiry and contact forms", "Website pages and enquiry reference code")),
        ("L", 620, "Studio Employee", ("Login, status and note updates on own work", "Assigned enquiries and projects")),
        ("L", 1050, "Studio Admin", ("Login, records, payments, settings, date range", "KPIs, charts, insights, forecast, reports")),
        ("R", 190, "Firebase Realtime Database", ("REST PUT of the table bundle", "REST GET sync summary")),
        ("R", 620, "Local Data Folder (JSON, CSV, Excel)", ("JSON, CSV and Excel exports", "Last exported bundle")),
        ("R", 1050, "Render Web Service (hosting)", ("200 OK for the health check", "GET /health requests")),
    ]
    for side, y, label, (first, second) in ents:
        if side == "L":
            x0, x1 = 30, 330
            c.box(x0, y - 70, x1, y + 70, label, 33, True, fill=W, width=4)
            c.arrow([(x1, y - 26), (px0, y - 26)], first, lp=((x1 + px0) / 2, y - 76), lsize=25, lmax=300)
            c.arrow([(px0, y + 30), (x1, y + 30)], second, lp=((x1 + px0) / 2, y + 82), lsize=25, lmax=300)
        else:
            x0, x1 = 1470, 1770
            c.box(x0, y - 70, x1, y + 70, label, 33, True, fill=W, width=4)
            c.arrow([(px1, y - 26), (x0, y - 26)], first, lp=((px1 + x0) / 2, y - 76), lsize=25, lmax=300)
            c.arrow([(x0, y + 30), (px1, y + 30)], second, lp=((px1 + x0) / 2, y + 82), lsize=25, lmax=300)
    c.save("01_context_diagram.png")


# =====================================================================
# 2. System architecture
# =====================================================================
def architecture():
    c = Canvas(1800, 1560)
    # layer frames
    def frame(y0, y1, title):
        c.d.rectangle((30, y0, 1770, y1), outline=K, width=4, fill=G1)
        c.text(380, y0 + 26, title, 30, True, anchor="tl")

    frame(20, 250, "Client tier: any modern browser")
    c.box(70, 90, 560, 220, "Public website\nJinja pages, Bootstrap 5.3.3", 30, False, fill=W)
    c.box(655, 90, 1145, 220, "Admin screens\nBootstrap and Chart.js 4.4.1", 30, False, fill=W)
    c.box(1240, 90, 1730, 220, "static/js/api.js\nfetch with X-CSRF-Token header", 30, False, fill=W)

    frame(330, 1085, "Application tier: Render service")
    c.box(70, 400, 1730, 530, "Flask 3 application factory app/__init__.py (Gunicorn, 1 worker, Python 3.12.8)\nbefore_request hooks: CSRF check, login gate  |  error handlers: 400, 401, 403, 404, 409, 413, 500", 30, True, fill=G2)
    c.box(70, 570, 560, 770, "13 route blueprints\npublic, auth, dashboard, customers, enquiries, bookings, services, payments, projects, analytics, reports, settings, sync", 26, False, fill=W)
    c.box(655, 570, 1145, 770, "Model layer app/models\nplain SQL, one connection per request, MySQL-style SQL normalised for SQLite in app/db.py", 26, False, fill=W)
    c.box(1240, 570, 1730, 770, "Validation and access control\nvalidators.py, authz.py (admin_required, employee_scope)", 26, False, fill=W)
    c.box(70, 820, 560, 1050, "Analytics package app/analytics\nloader.py reads SQL into Pandas; NumPy calculates; scikit-learn forecast; insights.py writes sentences", 26, False, fill=W)
    c.box(655, 820, 1145, 1050, "Reports app/reports\nfpdf2 for PDF, openpyxl for Excel, csv module for CSV", 26, False, fill=W)
    c.box(1240, 820, 1730, 1050, "Sync modules\nlocal_store.py writes JSON, CSV and Excel; firebase_sync.py calls Firebase REST", 26, False, fill=W)

    frame(1165, 1520, "Data tier")
    c.store(70, 1250, 560, 1440, "DB", "SQLite file instance/fotoinsight.db\n13 tables, foreign keys ON", 28)
    c.store(655, 1250, 1145, 1440, "FS", "data/ folder\nJSON, CSV, Excel for six tables and one bundle", 28)
    c.store(1240, 1250, 1730, 1440, "FB", "Firebase Realtime Database\nnode fotoinsight.json (external)", 28)

    # arrows between tiers
    c.arrow([(315, 220), (315, 400)], "HTTPS", lp=(380, 310), both=True)
    c.arrow([(900, 220), (900, 400)], "HTTPS", lp=(965, 310), both=True)
    c.arrow([(1485, 220), (1485, 400)], "JSON", lp=(1550, 310), both=True)
    c.arrow([(315, 530), (315, 570)], None)
    c.arrow([(900, 530), (900, 570)], None)
    c.arrow([(1485, 530), (1485, 570)], None)
    c.arrow([(560, 670), (655, 670)], None, both=True)
    c.arrow([(1145, 670), (1240, 670)], None, both=True)
    c.arrow([(315, 770), (315, 820)], None)
    c.arrow([(900, 770), (900, 820)], None)
    c.arrow([(1485, 770), (1485, 820)], None)
    c.arrow([(315, 1050), (315, 1250)], "SQL read", lp=(400, 1150), both=True)
    c.arrow([(900, 1050), (900, 1250)], None, both=True)
    c.arrow([(1400, 1050), (1050, 1250)], "writes files", lp=(1260, 1150))
    c.arrow([(1600, 1050), (1600, 1250)], "REST PUT / GET", lp=(1660, 1150), both=True)
    c.save("02_system_architecture.png")


# =====================================================================
# 3. SDLC flowchart
# =====================================================================
def sdlc():
    c = Canvas(1800, 860)
    stages = [
        ("1. Requirement analysis", "Days 1 to 4\nStudio workflow, tracked data, metric definitions"),
        ("2. System design", "Days 5 to 9\n13-table schema, routes, analytics rules, screens"),
        ("3. Iterative coding", "Days 10 to 36\nFive build phases, one module at a time"),
        ("4. Integration", "Days 37 to 39\nBlueprints, models, Pandas layer and Chart.js joined"),
        ("5. Testing and debugging", "Days 40 to 45\npytest, manual security checks, fixes"),
        ("6. Render deployment", "After handover\nSQLite seed on build, Gunicorn, /health check"),
        ("7. Maintenance", "Ongoing\nData export, Firebase sync, rule updates"),
    ]
    bw, bh = 360, 250
    pos = [(50, 90), (490, 90), (930, 90), (1370, 90), (1370, 540), (930, 540), (490, 540)]
    for (title, sub), (x, y) in zip(stages, pos):
        c.d.rounded_rectangle((x, y, x + bw, y + bh), radius=22, fill=G1, outline=K, width=4)
        c.text(x + bw / 2, y + 52, title, 31, True, maxw=bw - 30)
        c.text(x + bw / 2, y + 160, sub, 26, False, maxw=bw - 40)
    for i in range(3):
        c.arrow([(pos[i][0] + bw, pos[i][1] + bh / 2), (pos[i + 1][0], pos[i + 1][1] + bh / 2)])
    c.arrow([(pos[3][0] + bw / 2, pos[3][1] + bh), (pos[3][0] + bw / 2, pos[4][1])])
    c.arrow([(pos[4][0], pos[4][1] + bh / 2), (pos[5][0] + bw, pos[5][1] + bh / 2)])
    c.arrow([(pos[5][0], pos[5][1] + bh / 2), (pos[6][0] + bw, pos[6][1] + bh / 2)])
    c.box(50, 540, 410, 790, "Handover\nWorking application, source code and report", 28, False, fill=W, width=3, radius=22)
    c.arrow([(pos[6][0], pos[6][1] + bh / 2), (410, pos[6][1] + bh / 2)], dash=True)
    c.arrow([(1420, 540), (1420, 440), (1160, 440), (1160, 340)], dash=True)
    c.tag(1130, 478, "Agile feedback loop: defects found in testing return to coding", 25, 380)
    c.save("03_sdlc_flowchart.png")


# =====================================================================
# 4. DFD level 1
# =====================================================================
def dfd_l1():
    c = Canvas(1800, 1580)

    def ent(x0, y0, x1, y1, text, dup=False):
        c.box(x0, y0, x1, y1, text, 32, True, fill=W, width=4)
        if dup:
            c.d.polygon([(x0, y0), (x0 + 34, y0), (x0, y0 + 34)], fill=K)

    def proc(box, num, text):
        x0, y0, x1, y1 = box
        c.d.rounded_rectangle(box, radius=26, fill=G2, outline=K, width=4)
        c.text((x0 + x1) / 2, y0 + 36, num, 32, True)
        c.text((x0 + x1) / 2, (y0 + y1) / 2 + 22, text, 28, False, maxw=(x1 - x0) - 30)

    P = {
        1: (560, 40, 940, 230), 2: (560, 290, 940, 480), 3: (560, 540, 940, 780),
        4: (560, 850, 940, 1040), 5: (560, 1110, 940, 1300), 6: (560, 1360, 940, 1520),
    }
    names = {
        1: "Authentication and session control", 2: "Public enquiry and contact capture",
        3: "CRM records: customers, enquiries, bookings, services", 4: "Payments and project tracking",
        5: "Analytics engine (Pandas, NumPy, scikit-learn)", 6: "Reports, export and cloud sync",
    }
    for k in P:
        proc(P[k], f"{k}.0", names[k])
    ent(30, 70, 300, 200, "Studio Staff\n(Admin, Employee)", dup=True)
    ent(30, 320, 300, 460, "Visitor / Client")
    ent(30, 540, 300, 1520, "Studio Staff\n(Admin, Employee)", dup=True)

    S = {
        "D1": (1250, 80, 1690, 180, "Users and employees"),
        "D2": (1250, 290, 1690, 390, "Customers, enquiries and notes"),
        "D5": (1250, 470, 1690, 570, "Services, packages and settings"),
        "D3": (1250, 650, 1690, 750, "Bookings, team and projects"),
        "D4": (1250, 900, 1690, 1000, "Payments"),
        "D6": (1250, 1420, 1690, 1520, "Local files and Firebase copy"),
    }
    for key, (x0, y0, x1, y1, t) in S.items():
        c.store(x0, y0, x1, y1, key, t, 27)

    L = 26
    # staff / auth
    c.arrow([(300, 110), (560, 110)], "Login form", lp=(430, 82))
    c.arrow([(560, 170), (300, 170)], "Session cookie, role", lp=(430, 204), lmax=250)
    # visitor / public capture
    c.arrow([(300, 355), (560, 355)], "Enquiry and contact forms", lp=(430, 322), lmax=250)
    c.arrow([(560, 430), (300, 430)], "Reference code", lp=(430, 462), lmax=250)
    # staff / CRM
    c.arrow([(300, 600), (560, 600)], "Create, edit, convert records", lp=(430, 568), lmax=250)
    c.arrow([(560, 730), (300, 730)], "Lists, details, search", lp=(430, 762), lmax=250)
    # staff / payments
    c.arrow([(300, 900), (560, 900)], "Payments, project status", lp=(430, 868), lmax=250)
    c.arrow([(560, 990), (300, 990)], "Balances, project list", lp=(430, 1022), lmax=250)
    # staff / analytics
    c.arrow([(300, 1160), (560, 1160)], "Date range", lp=(430, 1130))
    c.arrow([(560, 1250), (300, 1250)], "KPIs, charts, insights, forecast", lp=(430, 1286), lmax=250)
    # staff / reports
    c.arrow([(300, 1410), (560, 1410)], "Report and sync requests", lp=(430, 1378), lmax=250)
    c.arrow([(560, 1490), (300, 1490)], "Files, sync status", lp=(430, 1522), lmax=250)

    # process <-> stores
    c.arrow([(940, 130), (1250, 130)], "Verify password, load role", lp=(1095, 100), lmax=300, both=True)
    c.arrow([(940, 310), (1250, 310)], "New enquiry and customer", lp=(1095, 280), lmax=300)
    c.arrow([(940, 580), (1100, 580), (1100, 375), (1250, 375)], "CRM rows", lp=(1100, 470), lmax=130, both=True)
    c.arrow([(940, 620), (1180, 620), (1180, 540), (1250, 540)], None, both=True)
    c.arrow([(940, 700), (1250, 700)], None, both=True)
    c.arrow([(940, 880), (1120, 880), (1120, 735), (1250, 735)], None, both=True)
    c.arrow([(940, 960), (1250, 960)], "Payment rows", lp=(1095, 930), lmax=300, both=True)

    # analytics / export bus
    bus_x = 1745
    for y in (340, 520, 700, 950):
        c.line([(1690, y), (bus_x, y)])
        c.d.ellipse((bus_x - 7, y - 7, bus_x + 7, y + 7), fill=K)
    c.line([(bus_x, 340), (bus_x, 1390)])
    c.arrow([(bus_x, 1190), (940, 1190)])
    c.tag(1380, 1160, "Business tables read for analysis", 26, 380)
    c.arrow([(bus_x, 1390), (940, 1390)])
    c.tag(1380, 1360, "Rows read for export", 26, 380)
    c.d.ellipse((bus_x - 7, 1190 - 7, bus_x + 7, 1190 + 7), fill=K)
    c.arrow([(940, 1470), (1250, 1470)], "JSON, CSV, Excel, REST PUT", lp=(1095, 1438), lmax=300)
    c.save("04_dfd_level1.png")


# =====================================================================
# helpers for level-2 diagrams
# =====================================================================
def proc_box(c, box, num, text, size=27):
    x0, y0, x1, y1 = box
    c.d.rounded_rectangle(box, radius=26, fill=G2, outline=K, width=4)
    c.text((x0 + x1) / 2, y0 + 34, num, 31, True)
    c.text((x0 + x1) / 2, (y0 + y1) / 2 + 22, text, size, False, maxw=(x1 - x0) - 28)


def entity_box(c, box, text, dup=False):
    x0, y0, x1, y1 = box
    c.box(x0, y0, x1, y1, text, 31, True, fill=W, width=4)
    if dup:
        c.d.polygon([(x0, y0), (x0 + 32, y0), (x0, y0 + 32)], fill=K)


# =====================================================================
# 5. ERD
# =====================================================================
TABLES = {
    "employees": ["PK id", "full_name", "email, phone", "job_title, city", "status", "is_demo"],
    "users": ["PK id", "username (UK)", "email (UK)", "password_hash", "role: admin | employee", "FK employee_id", "is_active"],
    "business_settings": ["PK id (always 1)", "business_name, tagline", "email, phone, address", "city, map_lat, map_lng", "instagram, facebook, youtube", "about_intro, mission, vision"],
    "customers": ["PK id", "full_name", "email, phone", "city, address", "registration_date", "is_demo"],
    "enquiries": ["PK id", "enquiry_code (UK)", "FK customer_id", "FK package_id", "FK assigned_employee_id", "event_type, event_date", "city, guest_count, budget", "status", "submission_token (UK)"],
    "enquiry_notes": ["PK id", "FK enquiry_id", "FK user_id", "note", "created_at"],
    "customer_feedback": ["PK id", "FK customer_id", "FK booking_id", "rating (1 to 5)", "comment", "is_public"],
    "bookings": ["PK id", "booking_code (UK)", "FK customer_id", "FK enquiry_id (UK)", "FK service_id", "FK package_id", "event_date, city", "total_amount (> 0)", "status"],
    "booking_team": ["PK id", "FK booking_id", "FK employee_id", "team_role", "is_lead"],
    "services": ["PK id", "name (UK)", "slug (UK)", "category", "base_price", "status, sort_order"],
    "payments": ["PK id", "payment_code (UK)", "FK booking_id", "FK recorded_by", "amount (> 0)", "payment_date", "method", "status", "transaction_ref"],
    "projects": ["PK id", "project_code (UK)", "FK booking_id (UK)", "FK photographer_id", "FK editor_id", "start_date, delivery_date", "status"],
    "packages": ["PK id", "FK service_id", "name", "price", "inclusions", "status"],
}


def erd():
    BW, HEAD, LH = 540, 58, 40
    grid = {
        "employees": (0, 0), "users": (1, 0), "business_settings": (2, 0),
        "customers": (0, 1), "enquiries": (1, 1), "enquiry_notes": (2, 1),
        "customer_feedback": (0, 2), "bookings": (1, 2), "booking_team": (2, 2),
        "services": (0, 3), "payments": (1, 3), "projects": (2, 3),
        "packages": (0, 4),
    }
    xs = [40, 630, 1220]
    row_y = [40, 470, 960, 1440, 1960]
    rect = {}
    c = Canvas(1800, 2420)
    for name, (cx_, ry) in grid.items():
        x0 = xs[cx_]
        y0 = row_y[ry]
        h = HEAD + LH * len(TABLES[name]) + 14
        rect[name] = (x0, y0, x0 + BW, y0 + h)

    def edge_pt(r, tx, ty):
        x0, y0, x1, y1 = r
        cx_, cy_ = (x0 + x1) / 2, (y0 + y1) / 2
        dx, dy = tx - cx_, ty - cy_
        if dx == 0 and dy == 0:
            return cx_, cy_
        sx = (x1 - x0) / 2 / abs(dx) if dx else 1e9
        sy = (y1 - y0) / 2 / abs(dy) if dy else 1e9
        t = min(sx, sy)
        return cx_ + dx * t, cy_ + dy * t

    def rel(a, b, ca, cb):
        ra, rb = rect[a], rect[b]
        ca_pt = ((ra[0] + ra[2]) / 2, (ra[1] + ra[3]) / 2)
        cb_pt = ((rb[0] + rb[2]) / 2, (rb[1] + rb[3]) / 2)
        pa = edge_pt(ra, *cb_pt)
        pb = edge_pt(rb, *ca_pt)
        c.line([pa, pb], 4)
        for pt, other, card in ((pa, pb, ca), (pb, pa, cb)):
            dx, dy = other[0] - pt[0], other[1] - pt[1]
            ln = math.hypot(dx, dy) or 1
            ux, uy = dx / ln, dy / ln
            px, py = -uy, ux
            if card == "N":
                base = (pt[0] + ux * 26, pt[1] + uy * 26)
                for k in (-1, 0, 1):
                    c.d.line((pt[0] + px * 14 * k, pt[1] + py * 14 * k, base[0], base[1]), fill=K, width=4)
                lbl = (pt[0] + ux * 52 + px * 24, pt[1] + uy * 52 + py * 24)
                c.text(lbl[0], lbl[1], "N", 28, True)
            else:
                bar = (pt[0] + ux * 22, pt[1] + uy * 22)
                c.d.line((bar[0] + px * 14, bar[1] + py * 14, bar[0] - px * 14, bar[1] - py * 14), fill=K, width=5)
                lbl = (pt[0] + ux * 52 + px * 24, pt[1] + uy * 52 + py * 24)
                c.text(lbl[0], lbl[1], card, 28, True)

    for name, r in rect.items():
        x0, y0, x1, y1 = r
        c.d.rectangle(r, fill=W, outline=K, width=4)
        c.d.rectangle((x0, y0, x1, y0 + HEAD), fill=G2, outline=K, width=4)
        c.text((x0 + x1) / 2, y0 + HEAD / 2, name, 33, True)
        for i, row in enumerate(TABLES[name]):
            bold = row.startswith("PK")
            c.text(x0 + 20, y0 + HEAD + 10 + i * LH + LH / 2 - 4, row, 27, bold, anchor="l")
    rel("employees", "users", "1", "N")
    rel("users", "enquiry_notes", "1", "N")
    rel("customers", "enquiries", "1", "N")
    rel("enquiries", "enquiry_notes", "1", "N")
    rel("enquiries", "bookings", "1", "0..1")
    rel("customers", "bookings", "1", "N")
    rel("customers", "customer_feedback", "1", "N")
    rel("customer_feedback", "bookings", "N", "1")
    rel("bookings", "booking_team", "1", "N")
    rel("bookings", "payments", "1", "N")
    rel("bookings", "projects", "1", "0..1")
    rel("services", "bookings", "1", "N")
    rel("services", "packages", "1", "N")

    c.text(900, 2360, "PK primary key, FK foreign key, UK unique key.  1 = one, N = many (crow's foot), 0..1 = zero or one.\nSolid links show the main relationships; other foreign keys are listed inside each table.", 27, False, maxw=1650)
    c.save("05_erd.png")


# =====================================================================
# 6. Use-case diagram
# =====================================================================
def actor(c, cx, top, label):
    r = 26
    c.d.ellipse((cx - r, top, cx + r, top + 2 * r), outline=K, width=4, fill=W)
    c.line([(cx, top + 2 * r), (cx, top + 2 * r + 70)], 4)
    c.line([(cx - 48, top + 2 * r + 25), (cx + 48, top + 2 * r + 25)], 4)
    c.line([(cx, top + 2 * r + 70), (cx - 40, top + 2 * r + 130)], 4)
    c.line([(cx, top + 2 * r + 70), (cx + 40, top + 2 * r + 130)], 4)
    c.text(cx, top + 2 * r + 170, label, 30, True, maxw=250)


def use_case():
    c = Canvas(1800, 1780)
    c.d.rectangle((360, 30, 1440, 1690), outline=K, width=5)
    c.text(900, 70, "FotoInsight Studio Platform", 36, True)

    def uc(cx, cy, text, w=360, h=104):
        c.d.ellipse((cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2), fill=G1, outline=K, width=3)
        c.text(cx, cy, text, 24, False, maxw=w * 0.78)

    c.d.rectangle((410, 130, 1390, 620), outline=G4, width=3)
    c.text(520, 152, "Public website (no login)", 28, True, anchor="tl")
    pub = [
        (640, 270, "UC-01 Browse home, about, services, portfolio"),
        (640, 420, "UC-02 Submit event enquiry"),
        (640, 560, "UC-03 Send contact message"),
    ]
    for cx, cy, t in pub:
        uc(cx, cy, t)
    uc(1130, 420, "Duplicate protection by submission token", 380, 100)
    c.arrow([(820, 420), (940, 420)], "extend", lp=(880, 392), lsize=24, lmax=100, dash=True)
    uc(900, 700, "UC-04 Log in and log out (session cookie, CSRF token)", 520, 110)

    c.d.rectangle((400, 800, 890, 1670), outline=G4, width=3)
    c.text(420, 818, "Employee and admin\n(login required, includes UC-04)", 26, True, anchor="tl")
    c.d.rectangle((910, 800, 1400, 1670), outline=G4, width=3)
    c.text(930, 818, "Admin only\n(admin_required in code)", 26, True, anchor="tl")
    shared = [
        "UC-05 View overview KPIs and search",
        "UC-06 View customers, edit own ones",
        "UC-07 View enquiries, update status, add notes",
        "UC-08 View bookings and calendar",
        "UC-09 Track projects: update status and notes",
    ]
    admin = [
        "UC-10 Create, assign, convert and delete records",
        "UC-11 Record and edit payments",
        "UC-12 View analytics, insights and forecast",
        "UC-13 Download reports: PDF, Excel, CSV",
        "UC-14 Export files and sync to Firebase",
        "UC-15 Manage services, packages, settings, logins",
    ]
    for i, t in enumerate(shared):
        uc(645, 970 + i * 135, t, 440, 112)
    for i, t in enumerate(admin):
        uc(1155, 960 + i * 118, t, 440, 104)
    c.arrow([(900, 800), (900, 756)], "include", lp=(985, 778), lsize=24, lmax=100, dash=True)

    actor(c, 190, 360, "Visitor / Client")
    actor(c, 190, 1000, "Studio Employee")
    actor(c, 1610, 1100, "Studio Admin")
    for cx, cy, t in pub:
        c.line([(250, 470), (cx - 180, cy)], 3)
    c.line([(250, 1100), (400, 1100)], 3)
    c.line([(1560, 1200), (1400, 1200)], 3)
    c.line([(1560, 1200), (1160, 760), (1160, 756)], 3) if False else None
    c.line([(1560, 1200), (1420, 1100), (1160, 756)], 3) if False else None
    # generalisation: admin is also an employee
    c.arrow([(1610, 1300 + 60), (1610, 1735), (190, 1735), (190, 1258)], "Studio Admin is also an employee, so it inherits UC-05 to UC-09", lp=(900, 1760), lsize=26, lmax=1200)
    c.save("06_use_case_diagram.png")


# =====================================================================
# 7. Deployment flow
# =====================================================================
def deployment():
    c = Canvas(1800, 1240)
    def card(x, y, w, h, title, sub, fill=G1):
        c.d.rounded_rectangle((x, y, x + w, y + h), radius=22, fill=fill, outline=K, width=4)
        c.text(x + w / 2, y + 44, title, 30, True, maxw=w - 30)
        c.text(x + w / 2, y + 44 + (h - 44) / 2, sub, 25, False, maxw=w - 36)

    card(40, 100, 360, 230, "Developer laptop", "Flask app, tests (pytest), database/seed_data.py")
    card(500, 100, 360, 230, "GitHub repository", "Madhavballabhkakkar/\nFotoInsight, branch main")
    card(960, 100, 360, 230, "Render build", "pip install -r\nrequirements.txt, then\nseed_data.py --reset")
    card(1420, 100, 340, 230, "Render start", 'gunicorn -w 1 -b 0.0.0.0:$PORT "wsgi:app"')
    c.arrow([(400, 215), (500, 215)], "git push", lp=(450, 170), lsize=24, lmax=100)
    c.arrow([(860, 215), (960, 215)], "auto deploy", lp=(910, 170), lsize=24, lmax=100)
    c.arrow([(1320, 215), (1420, 215)])

    card(1420, 520, 340, 230, "Health check", "GET /health returns status 200 before traffic is routed", G2)
    c.arrow([(1590, 330), (1590, 520)])
    card(960, 520, 380, 230, "Live website", "https://fotoinsight.onrender.com/ over HTTPS", G2)
    c.arrow([(1420, 635), (1340, 635)])
    card(500, 520, 380, 230, "Visitor or studio staff", "Any browser on desktop or mobile")
    c.arrow([(880, 635), (960, 635)], "HTTPS", lp=(920, 595), lmax=100, both=True)

    # configuration + data
    c.d.rectangle((40, 860, 880, 1150), fill=G1, outline=K, width=4)
    c.text(460, 895, "Environment variables (render.yaml)", 30, True)
    c.text(70, 940, "APP_ENV = production (secure session cookie)\nPYTHON_VERSION = 3.12.8\nSECRET_KEY = generated by Render\nSQLITE_PATH = instance/fotoinsight.db\nFIREBASE_DB_URL = optional\nFIREBASE_AUTH_TOKEN = optional", 27, False, anchor="tl", gap=10)
    c.store(960, 880, 1340, 1010, "DB", "SQLite file created by the seed script", 26)
    c.store(960, 1060, 1340, 1190, "FS", "data/ folder for JSON, CSV and Excel exports", 26)
    c.d.rounded_rectangle((1420, 880, 1760, 1190), radius=22, fill=W, outline=K, width=4)
    c.text(1590, 930, "Firebase Realtime Database", 30, True, maxw=300)
    c.text(1590, 1070, "Optional cloud copy through REST PUT and GET", 25, False, maxw=300)
    c.arrow([(1150, 750), (1150, 880)], "reads and writes", lp=(1150, 815), lmax=200, both=True)
    c.arrow([(1340, 1125), (1420, 1125)], "REST", lp=(1380, 1085), lsize=24, lmax=80)
    c.save("07_deployment_flow.png")


# =====================================================================
# 8-12. Level-2 DFDs
# =====================================================================
def dfd_auth():
    c = Canvas(1800, 1060)
    entity_box(c, (30, 250, 250, 1000), "Studio Staff\n(Admin, Employee)")
    c.store(660, 40, 1080, 150, "D1", "Users and employees", 28)
    P = {"1.1": (360, 250, 660, 500), "1.2": (760, 250, 1060, 500), "1.3": (1160, 250, 1460, 500)}
    proc_box(c, P["1.1"], "1.1", "Receive login form and check CSRF token")
    proc_box(c, P["1.2"], "1.2", "Find user, check password hash and active flag")
    proc_box(c, P["1.3"], "1.3", "Open session with user id, role, employee id")
    c.arrow([(250, 330), (360, 330)], "Login form\n+ token", lp=(305, 285), lsize=22, lmax=105)
    c.arrow([(360, 450), (250, 450)], "400 token\nerror", lp=(305, 490), lsize=22, lmax=105)
    c.arrow([(660, 375), (760, 375)], "Clean form", lp=(710, 330), lsize=22, lmax=110)
    c.arrow([(1060, 375), (1160, 375)], "Verified user", lp=(1110, 330), lsize=22, lmax=110)
    c.arrow([(900, 150), (900, 250)], "Look up username", lp=(1020, 200), lsize=22, lmax=200, both=True)
    c.arrow([(860, 500), (860, 580), (250, 580)], "401 wrong username or password", lp=(560, 545), lsize=24, lmax=420)
    c.arrow([(1310, 500), (1310, 650), (250, 650)], "Session cookie (HttpOnly, SameSite Lax, 8 hours) and redirect to dashboard", lp=(800, 612), lsize=24, lmax=620)
    P4 = (760, 780, 1060, 970)
    proc_box(c, P4, "1.4", "Gate every later request by session and role")
    c.arrow([(250, 840), (760, 840)], "Any page or API call with the session cookie", lp=(525, 800), lsize=24, lmax=400)
    c.arrow([(760, 925), (250, 925)], "401 sign in again, 403 role not allowed", lp=(525, 960), lsize=24, lmax=420)
    c.d.rounded_rectangle((1300, 790, 1760, 960), radius=22, fill=W, outline=K, width=4)
    c.text(1530, 875, "Route handlers 3.0 to 6.0\n(employees see only their own work)", 27, False, maxw=420)
    c.arrow([(1060, 875), (1300, 875)], "Allowed request", lp=(1180, 835), lsize=24, lmax=200)
    c.save("08_dfd_l2_auth.png")


def dfd_enquiry():
    c = Canvas(1800, 1220)
    entity_box(c, (30, 90, 250, 360), "Visitor / Client")
    entity_box(c, (30, 780, 250, 1000), "Studio Staff\n(Admin, Employee)")
    A = {"2.1": (370, 80, 670, 330), "2.2": (780, 80, 1080, 330), "2.3": (1190, 80, 1490, 330)}
    proc_box(c, A["2.1"], "2.1", "Validate and clean the form fields")
    proc_box(c, A["2.2"], "2.2", "Look for the same submission token")
    proc_box(c, A["2.3"], "2.3", "Create customer link and enquiry code")
    c.arrow([(250, 170), (370, 170)], "Enquiry form\n+ token", lp=(310, 125), lsize=22, lmax=115)
    c.arrow([(370, 285), (250, 285)], "400 field\nerrors", lp=(310, 322), lsize=22, lmax=110)
    c.arrow([(670, 205), (780, 205)], "Clean data", lp=(725, 165), lsize=22, lmax=110)
    c.arrow([(1080, 205), (1190, 205)], "New token", lp=(1135, 165), lsize=22, lmax=110)
    c.arrow([(930, 330), (930, 360), (180, 360)], "Existing reference code (duplicate = true)", lp=(560, 395), lsize=22, lmax=400)
    c.arrow([(1340, 80), (1340, 48), (140, 48), (140, 90)], "Reference code ENQ-nnnnn, 201 Created", lp=(740, 22), lsize=24, lmax=600)
    c.store(370, 470, 1490, 570, "D2", "Customers, enquiries and enquiry notes", 28)
    c.arrow([(930, 330), (930, 470)], "", lp=(0, 0), both=True)
    c.arrow([(1340, 330), (1340, 470)], "Insert customer, enquiry", lp=(1430, 400), lsize=22, lmax=170)
    c.arrow([(1490, 205), (1560, 205), (1560, 120), (330, 120)], "", lp=(0, 0)) if False else None
    c.arrow([(1490, 270), (1580, 270), (1580, 440), (330, 440), (330, 330)], "", lp=(0, 0)) if False else None
    # staff row
    B = {"3.1": (370, 700, 670, 950), "3.2": (780, 700, 1080, 950), "3.3": (1190, 700, 1490, 950)}
    proc_box(c, B["3.1"], "3.1", "Assign employee (admin) and add notes")
    proc_box(c, B["3.2"], "3.2", "Update enquiry status")
    proc_box(c, B["3.3"], "3.3", "Convert to booking (admin), once only")
    c.arrow([(250, 840), (370, 840)], "Edit\nrequest", lp=(310, 795), lsize=22, lmax=100)
    c.arrow([(670, 825), (780, 825)], "", lp=(0, 0))
    c.arrow([(1080, 825), (1190, 825)], "", lp=(0, 0))
    c.arrow([(520, 700), (520, 570)], "Read and write", lp=(615, 635), lsize=22, lmax=170, both=True)
    c.arrow([(930, 700), (930, 570)], "Status", lp=(980, 635), lsize=22, lmax=90, both=True)
    c.arrow([(1340, 700), (1340, 570)], "Status = converted", lp=(1450, 635), lsize=22, lmax=190)
    c.store(1190, 1060, 1760, 1160, "D3", "Bookings, team and projects", 28)
    c.arrow([(1340, 950), (1340, 1060)], "New booking row;\n409 if already converted", lp=(1535, 1010), lsize=22, lmax=240)
    c.arrow([(1190, 925), (290, 925)], "Booking code, or 409 conflict", lp=(740, 1000), lsize=22, lmax=360) if False else None
    c.save("09_dfd_l2_enquiry.png")


def dfd_payments():
    c = Canvas(1800, 1170)
    entity_box(c, (30, 230, 250, 1130), "Studio Staff\n(Admin, Employee)")
    c.store(700, 30, 1120, 130, "D3", "Bookings (total_amount)", 28)
    P = {"4.1": (360, 230, 660, 480), "4.2": (780, 230, 1080, 480), "4.3": (1200, 230, 1500, 480)}
    proc_box(c, P["4.1"], "4.1", "Validate amount, date, method and status")
    proc_box(c, P["4.2"], "4.2", "Compare with the booking balance")
    proc_box(c, P["4.3"], "4.3", "Save payment with a payment code")
    c.arrow([(250, 320), (360, 320)], "Payment\nform", lp=(305, 275), lsize=22, lmax=100)
    c.arrow([(360, 430), (250, 430)], "400\nerrors", lp=(305, 468), lsize=22, lmax=100)
    c.arrow([(660, 355), (780, 355)], "Valid\npayment", lp=(720, 305), lsize=22, lmax=100)
    c.arrow([(1080, 355), (1200, 355)], "Accepted", lp=(1140, 315), lsize=22, lmax=100)
    c.arrow([(930, 130), (930, 230)], "Contract value", lp=(1030, 180), lsize=22, lmax=160, both=True)
    c.arrow([(900, 480), (900, 560), (250, 560)], "409 payment is more than the contract balance", lp=(595, 595), lsize=22, lmax=480)
    c.store(1200, 580, 1760, 680, "D4", "Payments", 28)
    c.arrow([(1350, 480), (1350, 580)], "Insert", lp=(1400, 530), lsize=22, lmax=90)
    P44 = (1200, 780, 1500, 1020)
    proc_box(c, P44, "4.4", "Apply the signed revenue rule per row")
    c.arrow([(1350, 680), (1350, 780)], "Read all rows", lp=(1470, 730), lsize=22, lmax=170)
    c.arrow([(1350, 1020), (1350, 1090), (250, 1090)], "Collected, refunds, net revenue, outstanding", lp=(745, 1125), lsize=24, lmax=500)
    c.d.rounded_rectangle((1570, 800, 1770, 1010), radius=22, fill=G1, outline=K, width=4)
    c.text(1670, 905, "5.0 Analytics engine\n(signed amount\ncolumn)", 24, False, maxw=180)
    c.arrow([(1500, 905), (1570, 905)])
    c.d.rectangle((360, 700, 1100, 1040), fill=G1, outline=K, width=3)
    c.text(380, 715, "Revenue rule (signed amount)", 28, True, anchor="tl")
    c.text(380, 765, "paid and partially paid: + amount\nrefunded: - amount\npending: 0 (not counted)\n\nTest example: contract 100000, paid 30000,\npending 70000, refunded 5000\nNet revenue = 30000 - 5000 = 25000,\nand a 90000 payment returns 409", 25, False, anchor="tl", gap=8)
    c.save("10_dfd_l2_payments.png")


def dfd_analytics():
    c = Canvas(1800, 1200)
    entity_box(c, (30, 200, 250, 1160), "Studio Staff\n(browser)")
    c.store(580, 30, 1500, 130, "D2-D5", "customers, enquiries, bookings, payments, services", 27)
    P = {"5.1": (340, 210, 640, 470), "5.2": (720, 210, 1020, 470), "5.3": (1100, 210, 1400, 470), "5.4": (1480, 210, 1780, 470)}
    proc_box(c, P["5.1"], "5.1", "Resolve date range: preset or custom")
    proc_box(c, P["5.2"], "5.2", "Load tables into Pandas frames")
    proc_box(c, P["5.3"], "5.3", "Calculate metrics with NumPy")
    proc_box(c, P["5.4"], "5.4", "Forecast guard (scikit-learn)")
    c.arrow([(250, 340), (340, 340)], "Dates", lp=(295, 300), lsize=21, lmax=80)
    c.arrow([(640, 340), (720, 340)], "Start, end", lp=(680, 300), lsize=21, lmax=80)
    c.arrow([(1020, 340), (1100, 340)], "Frames", lp=(1060, 300), lsize=21, lmax=80)
    c.arrow([(1400, 340), (1480, 340)], "Monthly\nrevenue", lp=(1440, 295), lsize=21, lmax=80)
    c.arrow([(870, 130), (870, 210)], "SQL read", lp=(940, 170), lsize=22, lmax=110)
    P55 = (1100, 640, 1400, 900)
    proc_box(c, P55, "5.5", "Write insight sentences and package JSON")
    c.arrow([(1190, 470), (1190, 640)], "Metrics", lp=(1125, 540), lsize=22, lmax=90)
    c.arrow([(1630, 470), (1630, 560), (1310, 560), (1310, 640)], "Forecast or hidden message", lp=(1530, 600), lsize=22, lmax=240)
    c.arrow([(1250, 900), (1250, 1110), (250, 1110)], "JSON: KPIs, charts, insights, forecast", lp=(700, 1145), lsize=24, lmax=500)
    c.d.rectangle((340, 560, 1030, 1040), fill=G1, outline=K, width=3)
    c.text(360, 575, "Metrics produced by 5.3", 28, True, anchor="tl")
    c.text(360, 625, "Revenue = paid + partially paid - refunded\nConversion = converted / eligible x 100,\n  New enquiries are not counted as eligible\nCustomer segments: high value (top 25%),\n  returning (2 or more bookings), new\nService, location, seasonal and year tables\nGrowth against the previous period", 25, False, anchor="tl", gap=8)
    c.text(1450, 930, "Forecast is shown only with 8 or more\nmonths of history and R squared 0.15 or more", 24, False, anchor="tl", maxw=330)
    c.save("11_dfd_l2_analytics.png")


def dfd_sync():
    c = Canvas(1800, 1220)
    entity_box(c, (30, 200, 250, 1130), "Studio Admin")
    c.store(580, 30, 1260, 130, "D2-D5", "Business tables", 28)
    A = {"6.1": (360, 200, 660, 450), "6.2": (780, 200, 1080, 450)}
    proc_box(c, A["6.1"], "6.1", "Check admin role and report options")
    proc_box(c, A["6.2"], "6.2", "Build PDF, Excel or CSV file")
    c.arrow([(250, 280), (360, 280)], "Type,\nrange", lp=(305, 235), lsize=22, lmax=100)
    c.arrow([(660, 325), (780, 325)], "Options", lp=(720, 285), lsize=22, lmax=90)
    c.arrow([(930, 130), (930, 200)], "Read rows", lp=(1020, 165), lsize=22, lmax=110)
    c.arrow([(930, 450), (930, 520), (250, 520)], "Downloaded report file", lp=(590, 555), lsize=24, lmax=300)
    B = {"6.3": (360, 600, 660, 850), "6.4": (1180, 600, 1480, 850)}
    proc_box(c, B["6.3"], "6.3", "Export the six main tables to the data folder")
    proc_box(c, B["6.4"], "6.4", "Push bundle with REST PUT")
    c.arrow([(250, 725), (360, 725)], "Sync\nrequest", lp=(305, 680), lsize=22, lmax=100)
    c.store(740, 650, 1020, 800, "D6", "Local files\ndata/", 26)
    c.arrow([(660, 725), (740, 725)], "", lp=(0, 0))
    c.arrow([(1020, 725), (1180, 725)], "Bundle", lp=(1100, 685), lsize=22, lmax=100)
    c.arrow([(520, 130), (520, 130)], "", lp=(0, 0)) if False else None
    c.arrow([(1260, 100), (1520, 100), (1520, 300), (510, 300), (510, 600)], "", lp=(0, 0)) if False else None
    entity_box(c, (1540, 600, 1770, 1100), "Firebase\nRealtime\nDatabase")
    c.arrow([(1480, 700), (1540, 700)], "PUT", lp=(1510, 660), lsize=22, lmax=60)
    P65 = (1180, 940, 1480, 1170)
    proc_box(c, P65, "6.5", "Read cloud summary with REST GET")
    c.arrow([(1540, 1050), (1480, 1050)], "Summary", lp=(1510, 1010), lsize=22, lmax=70)
    c.arrow([(1180, 1050), (250, 1050)], "Row counts, table names, last sync time, status message", lp=(735, 1095), lsize=24, lmax=600)
    c.arrow([(520, 850), (520, 960), (250, 960)], "Export done: file list", lp=(405, 1000), lsize=22, lmax=190)
    c.save("12_dfd_l2_sync.png")


# =====================================================================
# 13. Status lifecycles
# =====================================================================
def lifecycles():
    c = Canvas(1800, 1440)

    def lane(y, title):
        c.d.rectangle((30, y, 1770, y + 300), fill=G1, outline=K, width=3)
        c.text(60, y + 24, title, 30, True, anchor="tl")

    def chip(cx, cy, t, w=250, fill=W):
        c.d.rounded_rectangle((cx - w / 2, cy - 38, cx + w / 2, cy + 38), radius=18, fill=fill, outline=K, width=3)
        c.text(cx, cy, t, 25, False, maxw=w - 20)

    def flow(a, b, y, w1=250, w2=250, label=""):
        c.arrow([(a + w1 / 2, y), (b - w2 / 2, y)], label, lp=((a + b) / 2, y - 34), lsize=21, lmax=100)

    # enquiry
    y = 30
    lane(y, "Enquiry status (enquiries.status)")
    ys = y + 140
    xs = [190, 520, 850, 1180, 1560]
    for x, t in zip(xs, ["New\n(not eligible)", "Contacted", "Follow-up\nRequired", "Negotiation", "Converted"]):
        chip(x, ys, t, 230, G2 if t == "Converted" else W)
    for a_, b_ in zip(xs, xs[1:]):
        flow(a_, b_, ys, 230, 230)
    chip(1180, ys + 110, "Rejected", 230, G2)
    c.arrow([(1180, ys + 38), (1180, ys + 72)], "", lp=(0, 0))
    c.text(500, ys + 112, "Conversion rate = Converted / eligible x 100\n(eligible = every status except New)", 24, False, maxw=700)
    # booking
    y = 360
    lane(y, "Booking status (bookings.status)")
    ys = y + 140
    chip(260, ys, "Confirmed", 260)
    chip(700, ys, "In Progress", 260)
    chip(1140, ys, "Completed", 260, G2)
    flow(260, 700, ys, 260, 260)
    flow(700, 1140, ys, 260, 260)
    chip(260, ys + 110, "On Hold", 260)
    chip(700, ys + 110, "Cancelled", 260, G2)
    c.arrow([(260, ys + 38), (260, ys + 72)], "", lp=(0, 0))
    c.arrow([(700, ys + 38), (700, ys + 72)], "", lp=(0, 0))
    c.text(1580, ys + 20, "A booking is created from an enquiry only once\n(bookings.enquiry_id is unique)", 24, False, maxw=330)
    # project
    y = 690
    lane(y, "Project status (projects.status)")
    ys = y + 140
    xs = [160, 440, 720, 1000, 1280, 1590]
    for x, t in zip(xs, ["Not Started", "In Progress", "Editing", "Review", "Completed", "Delivered"]):
        chip(x, ys, t, 220, G2 if t == "Delivered" else W)
    for a_, b_ in zip(xs, xs[1:]):
        flow(a_, b_, ys, 220, 220)
    c.text(900, ys + 100, "One project per booking (projects.booking_id is unique); photographer and editor are employees", 24, False, maxw=1500)
    # payment
    y = 1020
    lane(y, "Payment status (payments.status) and its sign in revenue")
    c.text(900, y + 85, "Net revenue = sum of signed amounts in the selected date range", 26, False, maxw=1500)
    ys = y + 170
    xs = [260, 700, 1140, 1570]
    labs = [("Paid", "+ amount"), ("Partially Paid", "+ amount"), ("Pending", "0 (ignored)"), ("Refunded", "- amount")]
    for x, (t, sg) in zip(xs, labs):
        chip(x, ys, t, 300, W)
        c.text(x, ys + 80, sg, 26, True)
    c.text(900, 1375, "Rounded boxes are statuses; arrows show the normal forward movement. Shaded boxes are end states.", 24, False, maxw=1600)
    c.save("13_status_lifecycles.png")


if __name__ == "__main__":
    context()
    architecture()
    sdlc()
    dfd_l1()
    erd()
    use_case()
    deployment()
    dfd_auth()
    dfd_enquiry()
    dfd_payments()
    dfd_analytics()
    dfd_sync()
    lifecycles()
