-- Create database
CREATE DATABASE IF NOT EXISTS sibersih 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

-- Use database
USE sibersih;

-- ========================================
-- Grant privileges (opsional, sesuaikan user)
-- ========================================
-- GRANT ALL PRIVILEGES ON sibersih.* TO 'your_user'@'localhost';
-- FLUSH PRIVILEGES;

-- ========================================
-- TABLES STRUCTURE
-- ========================================
-- Note: Tabel-tabel ini akan dibuat otomatis oleh Django migrations
-- Script ini hanya untuk referensi atau setup manual

-- ========================================
-- 1. AUTH & USERS TABLES
-- ========================================

-- Django Auth Tables
CREATE TABLE IF NOT EXISTS django_content_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE KEY django_content_type_app_label_model (app_label, model)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename VARCHAR(100) NOT NULL,
    UNIQUE KEY auth_permission_content_type_id_codename (content_type_id, codename),
    CONSTRAINT auth_permission_content_type_id_fk 
        FOREIGN KEY (content_type_id) REFERENCES django_content_type (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY auth_group_permissions_group_id_permission_id (group_id, permission_id),
    CONSTRAINT auth_group_permissions_group_id_fk FOREIGN KEY (group_id) REFERENCES auth_group (id),
    CONSTRAINT auth_group_permissions_permission_id_fk FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Custom User Model (accounts_customuser)
CREATE TABLE IF NOT EXISTS accounts_customuser (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6) NULL,
    is_superuser TINYINT(1) NOT NULL DEFAULT 0,
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    phone_number VARCHAR(15) NOT NULL,
    address TEXT NULL,
    role VARCHAR(10) NOT NULL DEFAULT 'user',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    is_staff TINYINT(1) NOT NULL DEFAULT 0,
    date_joined DATETIME(6) NOT NULL,
    profile_picture VARCHAR(100) NULL,
    INDEX accounts_customuser_username_idx (username),
    INDEX accounts_customuser_email_idx (email)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS accounts_customuser_groups (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customuser_id BIGINT NOT NULL,
    group_id INT NOT NULL,
    UNIQUE KEY accounts_customuser_groups_customuser_id_group_id (customuser_id, group_id),
    CONSTRAINT accounts_customuser_groups_customuser_id_fk 
        FOREIGN KEY (customuser_id) REFERENCES accounts_customuser (id),
    CONSTRAINT accounts_customuser_groups_group_id_fk 
        FOREIGN KEY (group_id) REFERENCES auth_group (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS accounts_customuser_user_permissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    customuser_id BIGINT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY accounts_customuser_user_permissions_customuser_id_permission_id (customuser_id, permission_id),
    CONSTRAINT accounts_customuser_user_permissions_customuser_id_fk 
        FOREIGN KEY (customuser_id) REFERENCES accounts_customuser (id),
    CONSTRAINT accounts_customuser_user_permissions_permission_id_fk 
        FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 2. PARTNERS TABLES
-- ========================================

-- COD Rate
CREATE TABLE IF NOT EXISTS partners_codrate (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    rate DECIMAL(5, 2) NOT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Laundry (Mitra)
CREATE TABLE IF NOT EXISTS partners_laundry (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    address TEXT NOT NULL,
    latitude DECIMAL(9, 6) NULL,
    longitude DECIMAL(9, 6) NULL,
    phone_number VARCHAR(15) NOT NULL,
    email VARCHAR(254) NULL,
    opening_hours VARCHAR(100) NULL,
    closing_hours VARCHAR(100) NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    rating DECIMAL(3, 2) NULL DEFAULT 0.00,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    owner_id BIGINT NOT NULL,
    map_link VARCHAR(500) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    CONSTRAINT partners_laundry_owner_id_fk 
        FOREIGN KEY (owner_id) REFERENCES accounts_customuser (id),
    INDEX partners_laundry_owner_id_idx (owner_id),
    INDEX partners_laundry_is_active_idx (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Laundry Images
CREATE TABLE IF NOT EXISTS partners_laundryimage (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    laundry_id BIGINT NOT NULL,
    image VARCHAR(100) NOT NULL,
    uploaded_at DATETIME(6) NOT NULL,
    CONSTRAINT partners_laundryimage_laundry_id_fk 
        FOREIGN KEY (laundry_id) REFERENCES partners_laundry (id) ON DELETE CASCADE,
    INDEX partners_laundryimage_laundry_id_idx (laundry_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Mitra Verification
CREATE TABLE IF NOT EXISTS partners_mitraverification (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id BIGINT NOT NULL UNIQUE,
    business_name VARCHAR(200) NOT NULL,
    business_address TEXT NOT NULL,
    id_card_number VARCHAR(20) NOT NULL,
    id_card_photo VARCHAR(100) NOT NULL,
    business_permit VARCHAR(100) NULL,
    phone_number VARCHAR(15) NOT NULL,
    email VARCHAR(254) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    rejection_reason TEXT NULL,
    submitted_at DATETIME(6) NOT NULL,
    verified_at DATETIME(6) NULL,
    verified_by_id BIGINT NULL,
    CONSTRAINT partners_mitraverification_user_id_fk 
        FOREIGN KEY (user_id) REFERENCES accounts_customuser (id),
    CONSTRAINT partners_mitraverification_verified_by_id_fk 
        FOREIGN KEY (verified_by_id) REFERENCES accounts_customuser (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Mitra Transactions
CREATE TABLE IF NOT EXISTS partners_mitratransaction (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    laundry_id BIGINT NOT NULL,
    order_id BIGINT NOT NULL UNIQUE,
    amount DECIMAL(10, 2) NOT NULL,
    admin_fee DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    net_amount DECIMAL(10, 2) NOT NULL,
    transaction_date DATETIME(6) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes TEXT NULL,
    CONSTRAINT partners_mitratransaction_laundry_id_fk 
        FOREIGN KEY (laundry_id) REFERENCES partners_laundry (id),
    INDEX partners_mitratransaction_laundry_id_idx (laundry_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 3. VOUCHERS TABLES
-- ========================================

-- Voucher
CREATE TABLE IF NOT EXISTS partners_voucher (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    code VARCHAR(20) NOT NULL UNIQUE,
    discount_type VARCHAR(10) NOT NULL,
    discount_value DECIMAL(10, 2) NOT NULL,
    max_discount DECIMAL(10, 2) NULL,
    min_transaction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    valid_from DATETIME(6) NOT NULL,
    valid_until DATETIME(6) NOT NULL,
    usage_limit INT NULL,
    used_count INT NOT NULL DEFAULT 0,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    description TEXT NULL,
    created_at DATETIME(6) NOT NULL,
    created_by_id BIGINT NULL,
    laundry_id BIGINT NULL,
    CONSTRAINT partners_voucher_created_by_id_fk 
        FOREIGN KEY (created_by_id) REFERENCES accounts_customuser (id),
    CONSTRAINT partners_voucher_laundry_id_fk 
        FOREIGN KEY (laundry_id) REFERENCES partners_laundry (id),
    INDEX partners_voucher_code_idx (code),
    INDEX partners_voucher_is_active_idx (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Voucher Request
CREATE TABLE IF NOT EXISTS partners_voucherrequest (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    laundry_id BIGINT NOT NULL,
    code VARCHAR(20) NOT NULL,
    discount_type VARCHAR(10) NOT NULL,
    discount_value DECIMAL(10, 2) NOT NULL,
    max_discount DECIMAL(10, 2) NULL,
    min_transaction DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    valid_from DATETIME(6) NOT NULL,
    valid_until DATETIME(6) NOT NULL,
    usage_limit INT NULL,
    description TEXT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    rejection_reason TEXT NULL,
    requested_at DATETIME(6) NOT NULL,
    reviewed_at DATETIME(6) NULL,
    reviewed_by_id BIGINT NULL,
    CONSTRAINT partners_voucherrequest_laundry_id_fk 
        FOREIGN KEY (laundry_id) REFERENCES partners_laundry (id),
    CONSTRAINT partners_voucherrequest_reviewed_by_id_fk 
        FOREIGN KEY (reviewed_by_id) REFERENCES accounts_customuser (id),
    INDEX partners_voucherrequest_laundry_id_idx (laundry_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 4. ORDERS TABLES
-- ========================================

-- Service
CREATE TABLE IF NOT EXISTS orders_service (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT NULL,
    base_price DECIMAL(10, 2) NOT NULL,
    unit VARCHAR(10) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Order
CREATE TABLE IF NOT EXISTS orders_order (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(20) NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
    laundry_id BIGINT NOT NULL,
    service_id BIGINT NOT NULL,
    weight DECIMAL(5, 2) NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    payment_method VARCHAR(20) NOT NULL DEFAULT 'cod',
    payment_status VARCHAR(20) NOT NULL DEFAULT 'unpaid',
    pickup_address TEXT NOT NULL,
    pickup_date DATE NOT NULL,
    pickup_time TIME NOT NULL,
    notes TEXT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    voucher_id BIGINT NULL,
    voucher_discount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    payment_proof VARCHAR(100) NULL,
    CONSTRAINT orders_order_user_id_fk 
        FOREIGN KEY (user_id) REFERENCES accounts_customuser (id),
    CONSTRAINT orders_order_laundry_id_fk 
        FOREIGN KEY (laundry_id) REFERENCES partners_laundry (id),
    CONSTRAINT orders_order_service_id_fk 
        FOREIGN KEY (service_id) REFERENCES orders_service (id),
    CONSTRAINT orders_order_voucher_id_fk 
        FOREIGN KEY (voucher_id) REFERENCES partners_voucher (id),
    INDEX orders_order_order_number_idx (order_number),
    INDEX orders_order_user_id_idx (user_id),
    INDEX orders_order_laundry_id_idx (laundry_id),
    INDEX orders_order_status_idx (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Payment
CREATE TABLE IF NOT EXISTS orders_payment (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE,
    payment_method VARCHAR(20) NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    payment_proof VARCHAR(100) NULL,
    payment_date DATETIME(6) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    notes TEXT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    verified_by_id BIGINT NULL,
    CONSTRAINT orders_payment_order_id_fk 
        FOREIGN KEY (order_id) REFERENCES orders_order (id) ON DELETE CASCADE,
    CONSTRAINT orders_payment_verified_by_id_fk 
        FOREIGN KEY (verified_by_id) REFERENCES accounts_customuser (id),
    INDEX orders_payment_order_id_idx (order_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Payment Issue
CREATE TABLE IF NOT EXISTS orders_paymentissue (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    payment_id BIGINT NOT NULL,
    issue_type VARCHAR(20) NOT NULL,
    description TEXT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'open',
    reported_at DATETIME(6) NOT NULL,
    resolved_at DATETIME(6) NULL,
    resolved_by_id BIGINT NULL,
    resolution_notes TEXT NULL,
    CONSTRAINT orders_paymentissue_payment_id_fk 
        FOREIGN KEY (payment_id) REFERENCES orders_payment (id) ON DELETE CASCADE,
    CONSTRAINT orders_paymentissue_resolved_by_id_fk 
        FOREIGN KEY (resolved_by_id) REFERENCES accounts_customuser (id),
    INDEX orders_paymentissue_payment_id_idx (payment_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Review
CREATE TABLE IF NOT EXISTS orders_review (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    order_id BIGINT NOT NULL UNIQUE,
    user_id BIGINT NOT NULL,
    laundry_id BIGINT NOT NULL,
    rating INT NOT NULL,
    comment TEXT NULL,
    created_at DATETIME(6) NOT NULL,
    updated_at DATETIME(6) NOT NULL,
    CONSTRAINT orders_review_order_id_fk 
        FOREIGN KEY (order_id) REFERENCES orders_order (id) ON DELETE CASCADE,
    CONSTRAINT orders_review_user_id_fk 
        FOREIGN KEY (user_id) REFERENCES accounts_customuser (id),
    CONSTRAINT orders_review_laundry_id_fk 
        FOREIGN KEY (laundry_id) REFERENCES partners_laundry (id),
    CONSTRAINT orders_review_rating_check CHECK (rating >= 1 AND rating <= 5),
    INDEX orders_review_laundry_id_idx (laundry_id),
    INDEX orders_review_user_id_idx (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- 5. DJANGO SYSTEM TABLES
-- ========================================

CREATE TABLE IF NOT EXISTS django_migrations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) NOT NULL PRIMARY KEY,
    session_data LONGTEXT NOT NULL,
    expire_date DATETIME(6) NOT NULL,
    INDEX django_session_expire_date_idx (expire_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

CREATE TABLE IF NOT EXISTS django_admin_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action_time DATETIME(6) NOT NULL,
    object_id LONGTEXT NULL,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT UNSIGNED NOT NULL,
    change_message LONGTEXT NOT NULL,
    content_type_id INT NULL,
    user_id BIGINT NOT NULL,
    CONSTRAINT django_admin_log_content_type_id_fk 
        FOREIGN KEY (content_type_id) REFERENCES django_content_type (id),
    CONSTRAINT django_admin_log_user_id_fk 
        FOREIGN KEY (user_id) REFERENCES accounts_customuser (id),
    INDEX django_admin_log_content_type_id_idx (content_type_id),
    INDEX django_admin_log_user_id_idx (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- ========================================
-- INITIAL DATA (OPTIONAL)
-- ========================================

-- Insert default services
INSERT INTO orders_service (name, description, base_price, unit, is_active, created_at, updated_at) VALUES
('Cuci Setrika', 'Layanan cuci dan setrika lengkap', 8000.00, 'kg', 1, NOW(), NOW()),
('Dry Clean', 'Pembersihan kering untuk pakaian khusus', 15000.00, 'pcs', 1, NOW(), NOW()),
('Cuci Ekspres', 'Layanan cuci cepat dalam 24 jam', 12000.00, 'kg', 1, NOW(), NOW()),
('Setrika Saja', 'Layanan setrika saja', 5000.00, 'kg', 1, NOW(), NOW()),
('Cuci Karpet', 'Layanan cuci karpet dan permadani', 20000.00, 'meter', 1, NOW(), NOW());

-- Insert default COD rate
INSERT INTO partners_codrate (rate, created_at, updated_at) VALUES
(5.00, NOW(), NOW());

-- ========================================
-- INDEXES FOR PERFORMANCE
-- ========================================

-- Additional indexes untuk query optimization
ALTER TABLE orders_order ADD INDEX idx_created_at (created_at);
ALTER TABLE orders_order ADD INDEX idx_pickup_date (pickup_date);
ALTER TABLE partners_laundry ADD INDEX idx_created_at (created_at);
ALTER TABLE partners_laundry ADD INDEX idx_rating (rating);
ALTER TABLE accounts_customuser ADD INDEX idx_role (role);
ALTER TABLE accounts_customuser ADD INDEX idx_date_joined (date_joined);

-- ========================================
-- VIEWS (OPTIONAL)
-- ========================================

-- View untuk statistik laundry
CREATE OR REPLACE VIEW view_laundry_stats AS
SELECT 
    l.id AS laundry_id,
    l.name AS laundry_name,
    COUNT(DISTINCT o.id) AS total_orders,
    COALESCE(SUM(o.total_price), 0) AS total_revenue,
    COALESCE(AVG(r.rating), 0) AS avg_rating,
    COUNT(DISTINCT r.id) AS total_reviews
FROM partners_laundry l
LEFT JOIN orders_order o ON l.id = o.laundry_id
LEFT JOIN orders_review r ON l.id = r.laundry_id
GROUP BY l.id, l.name;

-- View untuk statistik user
CREATE OR REPLACE VIEW view_user_stats AS
SELECT 
    u.id AS user_id,
    u.username,
    u.email,
    u.role,
    COUNT(DISTINCT o.id) AS total_orders,
    COALESCE(SUM(o.total_price), 0) AS total_spent
FROM accounts_customuser u
LEFT JOIN orders_order o ON u.id = o.user_id
GROUP BY u.id, u.username, u.email, u.role;

-- ========================================
-- STORED PROCEDURES (OPTIONAL)
-- ========================================

DELIMITER //

-- Procedure untuk update rating laundry
CREATE PROCEDURE update_laundry_rating(IN laundry_id_param BIGINT)
BEGIN
    DECLARE avg_rating DECIMAL(3,2);
    
    SELECT COALESCE(AVG(rating), 0) INTO avg_rating
    FROM orders_review
    WHERE laundry_id = laundry_id_param;
    
    UPDATE partners_laundry
    SET rating = avg_rating
    WHERE id = laundry_id_param;
END //

-- Procedure untuk generate order number
CREATE PROCEDURE generate_order_number(OUT order_num VARCHAR(20))
BEGIN
    DECLARE today_date VARCHAR(8);
    DECLARE sequence INT;
    
    SET today_date = DATE_FORMAT(NOW(), '%Y%m%d');
    
    SELECT COALESCE(MAX(CAST(SUBSTRING(order_number, 10) AS UNSIGNED)), 0) + 1 
    INTO sequence
    FROM orders_order
    WHERE order_number LIKE CONCAT('ORD', today_date, '%');
    
    SET order_num = CONCAT('ORD', today_date, LPAD(sequence, 4, '0'));
END //

DELIMITER ;

-- ========================================
-- TRIGGERS (OPTIONAL)
-- ========================================

DELIMITER //

-- Trigger untuk auto update laundry rating setelah review baru
CREATE TRIGGER after_review_insert
AFTER INSERT ON orders_review
FOR EACH ROW
BEGIN
    CALL update_laundry_rating(NEW.laundry_id);
END //

-- Trigger untuk auto update laundry rating setelah review diupdate
CREATE TRIGGER after_review_update
AFTER UPDATE ON orders_review
FOR EACH ROW
BEGIN
    CALL update_laundry_rating(NEW.laundry_id);
END //

-- Trigger untuk auto update voucher used_count
CREATE TRIGGER after_order_insert
AFTER INSERT ON orders_order
FOR EACH ROW
BEGIN
    IF NEW.voucher_id IS NOT NULL THEN
        UPDATE partners_voucher
        SET used_count = used_count + 1
        WHERE id = NEW.voucher_id;
    END IF;
END //

DELIMITER ;

-- ========================================
-- FINISH
-- ========================================

SELECT 'Database sibersih berhasil dibuat!' AS message;
SELECT 'Jalankan: python manage.py migrate' AS next_step;
