-- ============================================================
-- Smart Network Firewall with Basic IDS Features
-- MySQL Database Schema
-- ============================================================
-- How to use:
--   1. Open MySQL (Workbench, phpMyAdmin, or terminal)
--   2. Run this entire file
--   3. Update config.py / .env with your MySQL password
-- ============================================================

CREATE DATABASE IF NOT EXISTS smart_firewall
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE smart_firewall;

-- ----------------------------------------------------------
-- Table: admins
-- Passwords are inserted by the Flask app as secure hashes
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------
-- Table: firewall_rules
-- Simulation rules can block either an IP address or a port
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS firewall_rules (
    id INT AUTO_INCREMENT PRIMARY KEY,
    rule_type VARCHAR(10) NOT NULL,       -- IP / PORT
    value VARCHAR(45) NOT NULL,
    description VARCHAR(255),
    active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY unique_firewall_rule (rule_type, value)
);

-- Legacy table retained so older versions can be upgraded safely.
CREATE TABLE IF NOT EXISTS blocked_ips (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL UNIQUE,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------
-- Table: request_logs
-- Stores every simulated network request
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS request_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(45) NOT NULL,
    port INT NOT NULL,
    protocol VARCHAR(10) NOT NULL DEFAULT 'TCP',
    username VARCHAR(100),
    status VARCHAR(20) NOT NULL,          -- Allowed / Blocked
    alert VARCHAR(10) NOT NULL DEFAULT 'No', -- Yes / No
    failed_login TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------
-- Table: alerts
-- Stores IDS suspicious activity alerts
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS alerts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    log_id INT,
    ip_address VARCHAR(45) NOT NULL,
    reason VARCHAR(255) NOT NULL,
    severity VARCHAR(20) NOT NULL DEFAULT 'Medium',
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Optional sample rule for quick testing
INSERT IGNORE INTO firewall_rules (rule_type, value, description)
VALUES ('IP', '192.168.1.100', 'Sample blocked IP for classroom testing');
