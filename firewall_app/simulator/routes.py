"""Simulation-only request processing routes."""

import ipaddress

from flask import Blueprint, flash, redirect, render_template, request, url_for

from firewall_app.auth.routes import login_required
from utils.db import execute
from utils.firewall import check_request
from utils.ids import analyze_request

simulator_bp = Blueprint("simulator", __name__, url_prefix="/simulator")

PROTOCOLS = ("TCP", "UDP", "HTTP", "HTTPS", "ICMP")


@simulator_bp.route("/", methods=["GET", "POST"])
@login_required
def index():
    """Simulate a request through the firewall and IDS rules."""
    result = None

    if request.method == "POST":
        ip_address = request.form.get("ip_address", "").strip()
        port_text = request.form.get("port", "").strip()
        protocol = request.form.get("protocol", "TCP").upper()
        username = request.form.get("username", "").strip()
        failed_login = request.form.get("failed_login") == "on"

        try:
            ip_address = str(ipaddress.ip_address(ip_address))
            port = int(port_text)
            if not 1 <= port <= 65535:
                raise ValueError
            if protocol not in PROTOCOLS:
                raise ValueError
        except ValueError:
            flash("Enter a valid IP, port (1–65535), and protocol.", "warning")
            return redirect(url_for("simulator.index"))

        status, access_message, matched_rule = check_request(ip_address, port)

        log_id = execute(
            """
            INSERT INTO request_logs
                (ip_address, port, protocol, username, status, alert, failed_login)
            VALUES (%s, %s, %s, %s, %s, 'No', %s)
            """,
            (ip_address, port, protocol, username or None, status, failed_login),
        )

        alerts = analyze_request(
            log_id=log_id,
            ip_address=ip_address,
            status=status,
            failed_login=failed_login,
            matched_rule=matched_rule,
        )
        if alerts:
            execute("UPDATE request_logs SET alert = 'Yes' WHERE id = %s", (log_id,))

        result = {
            "ip_address": ip_address,
            "port": port,
            "protocol": protocol,
            "username": username or "Not provided",
            "status": status,
            "access_message": access_message,
            "matched_rule": matched_rule,
            "alerts": alerts,
            "failed_login": failed_login,
        }

        if alerts:
            flash("Request analyzed — suspicious activity was detected.", "danger")
        elif status == "Blocked":
            flash("Access denied by a simulated firewall rule.", "danger")
        else:
            flash("Access allowed. No suspicious activity detected.", "success")

    return render_template("simulator.html", result=result, protocols=PROTOCOLS)
