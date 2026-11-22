-- SQLite schema for FotoInsight (no external MySQL required).

PRAGMA foreign_keys = OFF;

DROP TABLE IF EXISTS customer_feedback;
DROP TABLE IF EXISTS enquiry_notes;
DROP TABLE IF EXISTS booking_team;
DROP TABLE IF EXISTS payments;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS bookings;
DROP TABLE IF EXISTS enquiries;
DROP TABLE IF EXISTS packages;
DROP TABLE IF EXISTS services;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS employees;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS business_settings;

PRAGMA foreign_keys = ON;

CREATE TABLE employees (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    job_title TEXT NOT NULL,
    city TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    role TEXT NOT NULL,
    employee_id INTEGER NULL REFERENCES employees(id) ON DELETE SET NULL,
    display_name TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    city TEXT NOT NULL,
    address TEXT NULL,
    registration_date TEXT NOT NULL,
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE services (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    slug TEXT NOT NULL UNIQUE,
    category TEXT NOT NULL,
    description TEXT NOT NULL,
    image_path TEXT NULL,
    base_price REAL NOT NULL CHECK (base_price >= 0),
    status TEXT NOT NULL DEFAULT 'active',
    sort_order INTEGER NOT NULL DEFAULT 0,
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE packages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    name TEXT NOT NULL,
    description TEXT NULL,
    price REAL NOT NULL CHECK (price >= 0),
    inclusions TEXT NULL,
    status TEXT NOT NULL DEFAULT 'active',
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE enquiries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enquiry_code TEXT NOT NULL UNIQUE,
    customer_id INTEGER NULL REFERENCES customers(id) ON DELETE RESTRICT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_date TEXT NULL,
    event_location TEXT NULL,
    city TEXT NULL,
    guest_count INTEGER NULL,
    package_id INTEGER NULL REFERENCES packages(id) ON DELETE SET NULL,
    estimated_budget REAL NULL,
    requirements TEXT NULL,
    status TEXT NOT NULL DEFAULT 'new',
    assigned_employee_id INTEGER NULL REFERENCES employees(id) ON DELETE SET NULL,
    submission_token TEXT NULL UNIQUE,
    source TEXT NOT NULL DEFAULT 'website',
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE enquiry_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enquiry_id INTEGER NOT NULL REFERENCES enquiries(id) ON DELETE CASCADE,
    user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE RESTRICT,
    note TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_code TEXT NOT NULL UNIQUE,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE RESTRICT,
    enquiry_id INTEGER NULL UNIQUE REFERENCES enquiries(id) ON DELETE RESTRICT,
    service_id INTEGER NOT NULL REFERENCES services(id) ON DELETE RESTRICT,
    package_id INTEGER NULL REFERENCES packages(id) ON DELETE SET NULL,
    event_name TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_date TEXT NOT NULL,
    event_location TEXT NOT NULL,
    city TEXT NOT NULL,
    total_amount REAL NOT NULL CHECK (total_amount > 0),
    status TEXT NOT NULL DEFAULT 'confirmed',
    notes TEXT NULL,
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE booking_team (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    employee_id INTEGER NOT NULL REFERENCES employees(id) ON DELETE RESTRICT,
    team_role TEXT NOT NULL,
    is_lead INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (booking_id, employee_id, team_role)
);

CREATE TABLE payments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    payment_code TEXT NOT NULL UNIQUE,
    booking_id INTEGER NOT NULL REFERENCES bookings(id) ON DELETE CASCADE,
    amount REAL NOT NULL CHECK (amount > 0),
    payment_date TEXT NOT NULL,
    method TEXT NOT NULL,
    transaction_ref TEXT NULL,
    status TEXT NOT NULL DEFAULT 'paid',
    notes TEXT NULL,
    recorded_by INTEGER NULL REFERENCES users(id) ON DELETE SET NULL,
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_code TEXT NOT NULL UNIQUE,
    booking_id INTEGER NOT NULL UNIQUE REFERENCES bookings(id) ON DELETE CASCADE,
    photographer_id INTEGER NULL REFERENCES employees(id) ON DELETE SET NULL,
    editor_id INTEGER NULL REFERENCES employees(id) ON DELETE SET NULL,
    start_date TEXT NULL,
    delivery_date TEXT NULL,
    status TEXT NOT NULL DEFAULT 'not_started',
    notes TEXT NULL,
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE customer_feedback (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
    booking_id INTEGER NULL REFERENCES bookings(id) ON DELETE SET NULL,
    rating INTEGER NOT NULL CHECK (rating BETWEEN 1 AND 5),
    comment TEXT NOT NULL,
    is_public INTEGER NOT NULL DEFAULT 0,
    is_demo INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE business_settings (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    business_name TEXT NOT NULL,
    tagline TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT NOT NULL,
    address TEXT NOT NULL,
    city TEXT NOT NULL,
    map_lat REAL NOT NULL,
    map_lng REAL NOT NULL,
    instagram_url TEXT NULL,
    facebook_url TEXT NULL,
    youtube_url TEXT NULL,
    about_intro TEXT NULL,
    mission TEXT NULL,
    vision TEXT NULL,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO business_settings (
    id, business_name, tagline, email, phone, address, city, map_lat, map_lng,
    instagram_url, facebook_url, youtube_url, about_intro, mission, vision
) VALUES (
    1,
    'FotoInsight Studio',
    'Wedding, celebration, and film — planned with care.',
    'hello@fotoinsight.demo',
    '+91 00000 00000',
    'Sample Studio Address, C-Scheme',
    'Jaipur',
    26.912400,
    75.787300,
    'https://instagram.com',
    'https://facebook.com',
    'https://youtube.com',
    'FotoInsight Studio plans, photographs, and delivers weddings, pre-wedding sessions, corporate events, and private celebrations. This website is the public face of the FotoInsight demonstration platform.',
    'To give every client a clear path from the first enquiry to the delivered film and album, with dates, people, and payments tracked in one place.',
    'A studio workflow that stays calm on the wedding day because the planning, the team, and the edit schedule were agreed before the event.'
);
