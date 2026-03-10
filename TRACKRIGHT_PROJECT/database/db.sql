-- MySQL schema for TrackRight

CREATE DATABASE IF NOT EXISTS trackright_db;
USE trackright_db;

-- Users table (Django handles this, but for reference)
-- Django auth_user table will be created by migrations

-- Products table
CREATE TABLE core_product (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    sku VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    quantity INT DEFAULT 0
);

-- Orders table
CREATE TABLE core_order (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_number VARCHAR(100) UNIQUE NOT NULL,
    customer_name VARCHAR(255) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Order Items table
CREATE TABLE core_orderitem (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    quantity INT,
    FOREIGN KEY (order_id) REFERENCES core_order(id),
    FOREIGN KEY (product_id) REFERENCES core_product(id)
);

-- Scan Logs table
CREATE TABLE core_scanlog (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    scanned_quantity INT,
    scanned_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (order_id) REFERENCES core_order(id),
    FOREIGN KEY (product_id) REFERENCES core_product(id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);

-- Mismatch Reports table
CREATE TABLE core_mismatchreport (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT,
    product_id INT,
    expected_quantity INT,
    actual_quantity INT,
    reported_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id INT,
    FOREIGN KEY (order_id) REFERENCES core_order(id),
    FOREIGN KEY (product_id) REFERENCES core_product(id),
    FOREIGN KEY (user_id) REFERENCES auth_user(id)
);