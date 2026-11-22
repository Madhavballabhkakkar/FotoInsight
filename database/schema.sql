-- FotoInsight relational schema.
-- Monetary columns use DECIMAL. Demo rows are flagged with is_demo = 1.
-- Synthetic records are not a real studio's financial history.

SET FOREIGN_KEY_CHECKS = 0;

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

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE employees (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(120) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    job_title VARCHAR(80) NOT NULL,
    city VARCHAR(80) NOT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    is_demo TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_employees_status (status),
    INDEX idx_employees_email (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL,
    email VARCHAR(150) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('admin', 'employee') NOT NULL,
    employee_id INT NULL,
    display_name VARCHAR(120) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_users_username (username),
    UNIQUE KEY uq_users_email (email),
    CONSTRAINT fk_users_employee FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE customers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    city VARCHAR(80) NOT NULL,
    address VARCHAR(255) NULL,
    registration_date DATE NOT NULL,
    is_demo TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_customers_name (full_name),
    INDEX idx_customers_email (email),
    INDEX idx_customers_phone (phone),
    INDEX idx_customers_city (city),
    INDEX idx_customers_registration (registration_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE services (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    slug VARCHAR(140) NOT NULL,
    category VARCHAR(80) NOT NULL,
    description TEXT NOT NULL,
    image_path VARCHAR(255) NULL,
    base_price DECIMAL(12, 2) NOT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    sort_order INT NOT NULL DEFAULT 0,
    is_demo TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_services_slug (slug),
    UNIQUE KEY uq_services_name (name),
    INDEX idx_services_status (status),
    CONSTRAINT chk_services_price CHECK (base_price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE packages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    service_id INT NOT NULL,
    name VARCHAR(150) NOT NULL,
    description TEXT NULL,
    price DECIMAL(12, 2) NOT NULL,
    inclusions TEXT NULL,
    status ENUM('active', 'inactive') NOT NULL DEFAULT 'active',
    is_demo TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT fk_packages_service FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE RESTRICT,
    INDEX idx_packages_status (status),
    CONSTRAINT chk_packages_price CHECK (price >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE enquiries (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enquiry_code VARCHAR(30) NOT NULL,
    customer_id INT NULL,
    full_name VARCHAR(150) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    event_type VARCHAR(80) NOT NULL,
    event_date DATE NULL,
    event_location VARCHAR(180) NULL,
    city VARCHAR(80) NULL,
    guest_count INT NULL,
    package_id INT NULL,
    estimated_budget DECIMAL(12, 2) NULL,
    requirements TEXT NULL,
    status ENUM('new', 'contacted', 'follow_up', 'negotiation', 'converted', 'rejected') NOT NULL DEFAULT 'new',
    assigned_employee_id INT NULL,
    submission_token VARCHAR(64) NULL,
    source ENUM('website', 'admin', 'contact') NOT NULL DEFAULT 'website',
    is_demo TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_enquiries_code (enquiry_code),
    UNIQUE KEY uq_enquiries_token (submission_token),
    INDEX idx_enquiries_status (status),
    INDEX idx_enquiries_event_date (event_date),
    INDEX idx_enquiries_event_type (event_type),
    INDEX idx_enquiries_created (created_at),
    INDEX idx_enquiries_city (city),
    CONSTRAINT fk_enquiries_customer FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE RESTRICT,
    CONSTRAINT fk_enquiries_package FOREIGN KEY (package_id) REFERENCES packages (id) ON DELETE SET NULL,
    CONSTRAINT fk_enquiries_employee FOREIGN KEY (assigned_employee_id) REFERENCES employees (id) ON DELETE SET NULL,
    CONSTRAINT chk_enquiries_guests CHECK (guest_count IS NULL OR guest_count >= 0),
    CONSTRAINT chk_enquiries_budget CHECK (estimated_budget IS NULL OR estimated_budget >= 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE enquiry_notes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    enquiry_id INT NOT NULL,
    user_id INT NOT NULL,
    note TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_notes_enquiry FOREIGN KEY (enquiry_id) REFERENCES enquiries (id) ON DELETE CASCADE,
    CONSTRAINT fk_notes_user FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE RESTRICT,
    INDEX idx_notes_enquiry (enquiry_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE bookings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_code VARCHAR(30) NOT NULL,
    customer_id INT NOT NULL,
    enquiry_id INT NULL,
    service_id INT NOT NULL,
    package_id INT NULL,
    event_name VARCHAR(180) NOT NULL,
    event_type VARCHAR(80) NOT NULL,
    event_date DATE NOT NULL,
    event_location VARCHAR(180) NOT NULL,
    city VARCHAR(80) NOT NULL,
    total_amount DECIMAL(12, 2) NOT NULL,
    status ENUM('confirmed', 'in_progress', 'completed', 'cancelled', 'on_hold') NOT NULL DEFAULT 'confirmed',
    notes TEXT NULL,
    is_demo TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_bookings_code (booking_code),
    UNIQUE KEY uq_bookings_enquiry (enquiry_id),
    INDEX idx_bookings_event_date (event_date),
    INDEX idx_bookings_status (status),
    INDEX idx_bookings_city (city),
    INDEX idx_bookings_created (created_at),
    CONSTRAINT fk_bookings_customer FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE RESTRICT,
    CONSTRAINT fk_bookings_enquiry FOREIGN KEY (enquiry_id) REFERENCES enquiries (id) ON DELETE RESTRICT,
    CONSTRAINT fk_bookings_service FOREIGN KEY (service_id) REFERENCES services (id) ON DELETE RESTRICT,
    CONSTRAINT fk_bookings_package FOREIGN KEY (package_id) REFERENCES packages (id) ON DELETE SET NULL,
    CONSTRAINT chk_bookings_total CHECK (total_amount > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE booking_team (
    id INT AUTO_INCREMENT PRIMARY KEY,
    booking_id INT NOT NULL,
    employee_id INT NOT NULL,
    team_role VARCHAR(60) NOT NULL,
    is_lead TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uq_booking_team (booking_id, employee_id, team_role),
    CONSTRAINT fk_team_booking FOREIGN KEY (booking_id) REFERENCES bookings (id) ON DELETE CASCADE,
    CONSTRAINT fk_team_employee FOREIGN KEY (employee_id) REFERENCES employees (id) ON DELETE RESTRICT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE payments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    payment_code VARCHAR(30) NOT NULL,
    booking_id INT NOT NULL,
    amount DECIMAL(12, 2) NOT NULL,
    payment_date DATE NOT NULL,
    method ENUM('upi', 'cash', 'bank_transfer', 'card', 'other') NOT NULL,
    transaction_ref VARCHAR(80) NULL,
    status ENUM('paid', 'pending', 'partially_paid', 'refunded') NOT NULL DEFAULT 'paid',
    notes VARCHAR(255) NULL,
    recorded_by INT NULL,
    is_demo TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_payments_code (payment_code),
    INDEX idx_payments_date (payment_date),
    INDEX idx_payments_status (status),
    CONSTRAINT fk_payments_booking FOREIGN KEY (booking_id) REFERENCES bookings (id) ON DELETE CASCADE,
    CONSTRAINT fk_payments_user FOREIGN KEY (recorded_by) REFERENCES users (id) ON DELETE SET NULL,
    CONSTRAINT chk_payments_amount CHECK (amount > 0)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE projects (
    id INT AUTO_INCREMENT PRIMARY KEY,
    project_code VARCHAR(30) NOT NULL,
    booking_id INT NOT NULL,
    photographer_id INT NULL,
    editor_id INT NULL,
    start_date DATE NULL,
    delivery_date DATE NULL,
    status ENUM('not_started', 'in_progress', 'editing', 'review', 'completed', 'delivered') NOT NULL DEFAULT 'not_started',
    notes TEXT NULL,
    is_demo TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_projects_code (project_code),
    UNIQUE KEY uq_projects_booking (booking_id),
    INDEX idx_projects_status (status),
    INDEX idx_projects_delivery (delivery_date),
    CONSTRAINT fk_projects_booking FOREIGN KEY (booking_id) REFERENCES bookings (id) ON DELETE CASCADE,
    CONSTRAINT fk_projects_photographer FOREIGN KEY (photographer_id) REFERENCES employees (id) ON DELETE SET NULL,
    CONSTRAINT fk_projects_editor FOREIGN KEY (editor_id) REFERENCES employees (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE customer_feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT NOT NULL,
    booking_id INT NULL,
    rating TINYINT NOT NULL,
    comment TEXT NOT NULL,
    is_public TINYINT(1) NOT NULL DEFAULT 0,
    is_demo TINYINT(1) NOT NULL DEFAULT 0,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    CONSTRAINT fk_feedback_customer FOREIGN KEY (customer_id) REFERENCES customers (id) ON DELETE CASCADE,
    CONSTRAINT fk_feedback_booking FOREIGN KEY (booking_id) REFERENCES bookings (id) ON DELETE SET NULL,
    CONSTRAINT chk_feedback_rating CHECK (rating BETWEEN 1 AND 5)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE business_settings (
    id INT PRIMARY KEY,
    business_name VARCHAR(150) NOT NULL,
    tagline VARCHAR(255) NOT NULL,
    email VARCHAR(150) NOT NULL,
    phone VARCHAR(30) NOT NULL,
    address VARCHAR(255) NOT NULL,
    city VARCHAR(80) NOT NULL,
    map_lat DECIMAL(9, 6) NOT NULL,
    map_lng DECIMAL(9, 6) NOT NULL,
    instagram_url VARCHAR(255) NULL,
    facebook_url VARCHAR(255) NULL,
    youtube_url VARCHAR(255) NULL,
    about_intro TEXT NULL,
    mission TEXT NULL,
    vision TEXT NULL,
    updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CONSTRAINT chk_settings_single CHECK (id = 1)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

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
