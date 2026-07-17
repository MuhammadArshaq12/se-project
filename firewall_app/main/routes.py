"""Dashboard routes."""

from flask import Blueprint, render_template

from firewall_app.auth.routes import login_required
from utils.db import fetch_all, get_dashboard_data

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
@login_required
def dashboard():
    """Show live statistics, chart data, and recent IDS alerts."""
    dashboard_data = get_dashboard_data()
    recent_alerts = fetch_all(
        """
        SELECT id, ip_address, reason, severity, created_at
        FROM alerts
        ORDER BY created_at DESC
        LIMIT 5
        """
    )
    return render_template(
        "dashboard.html",
        stats=dashboard_data["stats"],
        status_chart=dashboard_data["status_chart"],
        traffic_chart=dashboard_data["traffic_chart"],
        recent_alerts=recent_alerts,
    )
