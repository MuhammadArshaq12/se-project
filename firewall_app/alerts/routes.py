"""IDS alert list routes."""

from flask import Blueprint, render_template, request

from firewall_app.auth.routes import login_required
from utils.db import fetch_all

alerts_bp = Blueprint("alerts", __name__, url_prefix="/alerts")


@alerts_bp.route("/")
@login_required
def index():
    """Display alerts with search and severity filters."""
    search = request.args.get("search", "").strip()
    severity = request.args.get("severity", "").strip().title()
    conditions = []
    params = []

    if search:
        conditions.append("(ip_address LIKE %s OR reason LIKE %s)")
        term = f"%{search}%"
        params.extend([term, term])
    if severity in {"Low", "Medium", "High", "Critical"}:
        conditions.append("severity = %s")
        params.append(severity)

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    alert_list = fetch_all(
        f"""
        SELECT id, log_id, ip_address, reason, severity, created_at
        FROM alerts
        {where_clause}
        ORDER BY created_at DESC
        """,
        tuple(params),
    )
    return render_template(
        "alerts.html",
        alerts=alert_list,
        search=search,
        severity=severity,
    )
