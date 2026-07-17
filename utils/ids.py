"""Beginner-friendly, rule-based IDS simulation service."""

from utils.db import execute, fetch_all, fetch_one


def create_alert(log_id, ip_address, reason, severity):
    """Save one IDS alert and return a dictionary for the result page."""
    execute(
        """
        INSERT INTO alerts (log_id, ip_address, reason, severity)
        VALUES (%s, %s, %s, %s)
        """,
        (log_id, ip_address, reason, severity),
    )
    return {"reason": reason, "severity": severity}


def analyze_request(log_id, ip_address, status, failed_login=False, matched_rule=None):
    """
    Analyze one simulated request using three simple IDS rules.

    Rule 1: Same IP makes more than 5 requests within one minute
    Rule 2: A blocked IP keeps sending requests
    Rule 3: 3 or more failed login attempts from the same IP

    Returns a list of generated alerts. An empty list means no IDS rule matched.
    """
    alerts = []

    # --------------------------------------------------
    # Rule 1: Too many requests from the same IP in 1 minute
    # The current request is already saved in request_logs,
    # so we count recent rows for this IP.
    # --------------------------------------------------
    recent = fetch_one(
        """
        SELECT COUNT(*) AS count
        FROM request_logs
        WHERE ip_address = %s
          AND created_at >= (NOW() - INTERVAL 1 MINUTE)
        """,
        (ip_address,),
    )
    if recent and recent["count"] > 5:
        reason = "More than 5 requests from the same IP within one minute"
        alerts.append(create_alert(log_id, ip_address, reason, "Medium"))

    # --------------------------------------------------
    # Rule 2: Blocked IP keeps sending requests
    # --------------------------------------------------
    if status == "Blocked":
        reason = f"Request matched blocked firewall rule: {matched_rule}"
        alerts.append(create_alert(log_id, ip_address, reason, "High"))

    # --------------------------------------------------
    # Rule 3: 3 failed login attempts (simulation)
    # Failed attempts are stored in request_logs, so the count survives
    # a server restart. Every third recent failure creates one alert.
    # --------------------------------------------------
    if failed_login:
        failed_count = fetch_one(
            """
            SELECT COUNT(*) AS count
            FROM request_logs
            WHERE ip_address = %s
              AND failed_login = 1
              AND created_at >= (NOW() - INTERVAL 10 MINUTE)
            """,
            (ip_address,),
        )["count"]
        if failed_count % 3 == 0:
            reason = "3 failed login attempts detected"
            alerts.append(create_alert(log_id, ip_address, reason, "High"))

    return alerts


def get_all_alerts():
    """Return all IDS alerts, newest first."""
    return fetch_all(
        """
        SELECT id, log_id, ip_address, reason, severity, created_at
        FROM alerts
        ORDER BY created_at DESC
        """
    )
