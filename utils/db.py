"""
Database helper functions.

This file keeps all MySQL connection and query logic in one place
so the rest of the app stays simple and readable.
"""

import pymysql
from pymysql.cursors import DictCursor
from datetime import date, timedelta
from werkzeug.security import generate_password_hash

from config import Config


def get_connection():
    """
    Create and return a new MySQL database connection.
    Callers should close the connection when finished.
    """
    return pymysql.connect(
        host=Config.DB_HOST,
        port=Config.DB_PORT,
        user=Config.DB_USER,
        password=Config.DB_PASSWORD,
        database=Config.DB_NAME,
        cursorclass=DictCursor,
        autocommit=True,
    )


def fetch_all(query, params=None):
    """Run a SELECT query and return all rows as a list of dictionaries."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchall()
    finally:
        connection.close()


def fetch_one(query, params=None):
    """Run a SELECT query and return a single row (or None)."""
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.fetchone()
    finally:
        connection.close()


def execute(query, params=None):
    """
    Run an INSERT / UPDATE / DELETE query.
    Returns the last inserted id when available.
    """
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute(query, params or ())
            return cursor.lastrowid
    finally:
        connection.close()


def _column_exists(table_name, column_name):
    """Return True when a column is already present in the configured database."""
    row = fetch_one(
        """
        SELECT COUNT(*) AS count
        FROM information_schema.COLUMNS
        WHERE TABLE_SCHEMA = %s AND TABLE_NAME = %s AND COLUMN_NAME = %s
        """,
        (Config.DB_NAME, table_name, column_name),
    )
    return bool(row["count"])


def ensure_database_schema():
    """
    Create new tables and safely upgrade the original project schema.

    Existing logs and alerts are preserved. This function is intentionally
    straightforward so students can see how a small schema migration works.
    """
    execute(
        """
        CREATE TABLE IF NOT EXISTS admins (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(80) NOT NULL UNIQUE,
            password_hash VARCHAR(255) NOT NULL,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    execute(
        """
        CREATE TABLE IF NOT EXISTS firewall_rules (
            id INT AUTO_INCREMENT PRIMARY KEY,
            rule_type VARCHAR(10) NOT NULL,
            value VARCHAR(45) NOT NULL,
            description VARCHAR(255) NULL,
            active TINYINT(1) NOT NULL DEFAULT 1,
            created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            UNIQUE KEY unique_firewall_rule (rule_type, value)
        )
        """
    )

    # Add fields introduced by the professional dashboard upgrade.
    request_columns = {
        "protocol": "VARCHAR(10) NOT NULL DEFAULT 'TCP'",
        "username": "VARCHAR(100) NULL",
        "failed_login": "TINYINT(1) NOT NULL DEFAULT 0",
    }
    for column, definition in request_columns.items():
        if not _column_exists("request_logs", column):
            execute(f"ALTER TABLE request_logs ADD COLUMN {column} {definition}")

    alert_columns = {
        "severity": "VARCHAR(20) NOT NULL DEFAULT 'Medium'",
        "log_id": "INT NULL",
    }
    for column, definition in alert_columns.items():
        if not _column_exists("alerts", column):
            execute(f"ALTER TABLE alerts ADD COLUMN {column} {definition}")

    # Preserve IPs from the original blocked_ips table as new firewall rules.
    execute(
        """
        INSERT IGNORE INTO firewall_rules (rule_type, value, description)
        SELECT 'IP', ip_address, 'Migrated from the original blocked IP list'
        FROM blocked_ips
        """
    )

    # Create a beginner-friendly default admin only when no account exists.
    admin_count = fetch_one("SELECT COUNT(*) AS count FROM admins")["count"]
    if admin_count == 0:
        execute(
            "INSERT INTO admins (username, password_hash) VALUES (%s, %s)",
            (
                Config.ADMIN_USERNAME,
                generate_password_hash(Config.ADMIN_PASSWORD),
            ),
        )


def get_dashboard_data():
    """
    Collect live statistics and Chart.js-ready data for the dashboard.
    """
    total = fetch_one("SELECT COUNT(*) AS count FROM request_logs")["count"]
    allowed = fetch_one(
        "SELECT COUNT(*) AS count FROM request_logs WHERE status = %s",
        ("Allowed",),
    )["count"]
    blocked = fetch_one(
        "SELECT COUNT(*) AS count FROM request_logs WHERE status = %s",
        ("Blocked",),
    )["count"]
    suspicious = fetch_one(
        "SELECT COUNT(*) AS count FROM request_logs WHERE alert = 'Yes'"
    )["count"]
    active_rules = fetch_one(
        "SELECT COUNT(*) AS count FROM firewall_rules WHERE active = 1"
    )["count"]

    daily_rows = fetch_all(
        """
        SELECT DATE(created_at) AS day, COUNT(*) AS count
        FROM request_logs
        WHERE created_at >= CURDATE() - INTERVAL 6 DAY
        GROUP BY DATE(created_at)
        """
    )
    daily_counts = {str(row["day"]): row["count"] for row in daily_rows}
    days = [date.today() - timedelta(days=offset) for offset in range(6, -1, -1)]

    return {
        "stats": {
            "total_requests": total,
            "allowed_requests": allowed,
            "blocked_requests": blocked,
            "suspicious_activities": suspicious,
            "active_rules": active_rules,
        },
        "status_chart": {
            "labels": ["Allowed", "Blocked"],
            "values": [allowed, blocked],
        },
        "traffic_chart": {
            "labels": [day.strftime("%b %d") for day in days],
            "values": [daily_counts.get(str(day), 0) for day in days],
        },
    }


def get_dashboard_stats():
    """Backward-compatible helper retained for simple classroom examples."""
    return get_dashboard_data()["stats"]
