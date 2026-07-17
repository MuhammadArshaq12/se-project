"""Simulation-only IP and port firewall rule service."""

from utils.db import execute, fetch_all, fetch_one


def get_rules():
    """Return every firewall rule, newest first."""
    return fetch_all(
        """
        SELECT id, rule_type, value, description, active, created_at
        FROM firewall_rules
        ORDER BY created_at DESC
        """
    )


def add_rule(rule_type, value, description=""):
    """Add a unique IP or port rule."""
    existing = fetch_one(
        "SELECT id FROM firewall_rules WHERE rule_type = %s AND value = %s",
        (rule_type, value),
    )
    if existing:
        return False, f"{rule_type} rule for {value} already exists."

    execute(
        """
        INSERT INTO firewall_rules (rule_type, value, description)
        VALUES (%s, %s, %s)
        """,
        (rule_type, value, description or None),
    )
    return True, f"{rule_type} rule for {value} was added."


def toggle_rule(rule_id):
    """Switch one firewall rule between active and inactive."""
    row = fetch_one(
        "SELECT value, active FROM firewall_rules WHERE id = %s",
        (rule_id,),
    )
    if not row:
        return False, "Firewall rule not found."

    new_state = 0 if row["active"] else 1
    execute("UPDATE firewall_rules SET active = %s WHERE id = %s", (new_state, rule_id))
    state_label = "enabled" if new_state else "disabled"
    return True, f"Rule for {row['value']} was {state_label}."


def delete_rule(rule_id):
    """Delete one firewall rule."""
    row = fetch_one("SELECT value FROM firewall_rules WHERE id = %s", (rule_id,))
    if not row:
        return False, "Firewall rule not found."
    execute("DELETE FROM firewall_rules WHERE id = %s", (rule_id,))
    return True, f"Rule for {row['value']} was deleted."


def check_request(ip_address, port):
    """
    Compare a simulated request against active IP and port rules.

    Returns:
        (status, message, matched_rule)
    """
    matched = fetch_one(
        """
        SELECT rule_type, value
        FROM firewall_rules
        WHERE active = 1
          AND (
              (rule_type = 'IP' AND value = %s)
              OR (rule_type = 'PORT' AND value = %s)
          )
        ORDER BY rule_type
        LIMIT 1
        """,
        (ip_address, str(port)),
    )
    if matched:
        rule_label = f"{matched['rule_type']} {matched['value']}"
        return "Blocked", "Access Denied", rule_label
    return "Allowed", "Access Allowed", None


# Compatibility helpers for students comparing this version with the original.
def get_blocked_ips():
    """Return active IP rules using the original field names."""
    return fetch_all(
        """
        SELECT id, value AS ip_address, created_at
        FROM firewall_rules
        WHERE rule_type = 'IP' AND active = 1
        ORDER BY created_at DESC
        """
    )


def is_ip_blocked(ip_address):
    """Return whether an active IP rule matches the supplied address."""
    return fetch_one(
        """
        SELECT id FROM firewall_rules
        WHERE rule_type = 'IP' AND value = %s AND active = 1
        """,
        (ip_address,),
    ) is not None
