"""Searchable request logs and CSV export routes."""

import csv
import io

from flask import Blueprint, Response, render_template, request

from firewall_app.auth.routes import login_required
from utils.db import fetch_all

logs_bp = Blueprint("logs", __name__, url_prefix="/logs")


def _read_filters():
    """Read supported filters from the query string."""
    return {
        "search": request.args.get("search", "").strip(),
        "status": request.args.get("status", "").strip(),
        "protocol": request.args.get("protocol", "").strip(),
        "alert": request.args.get("alert", "").strip(),
        "date": request.args.get("date", "").strip(),
    }


def _filtered_logs(filters):
    """Build a parameterized SQL query from optional filters."""
    conditions = []
    params = []

    if filters["search"]:
        conditions.append("(ip_address LIKE %s OR username LIKE %s)")
        term = f"%{filters['search']}%"
        params.extend([term, term])
    if filters["status"] in {"Allowed", "Blocked"}:
        conditions.append("status = %s")
        params.append(filters["status"])
    if filters["protocol"] in {"TCP", "UDP", "HTTP", "HTTPS", "ICMP"}:
        conditions.append("protocol = %s")
        params.append(filters["protocol"])
    if filters["alert"] in {"Yes", "No"}:
        conditions.append("alert = %s")
        params.append(filters["alert"])
    if filters["date"]:
        conditions.append("DATE(created_at) = %s")
        params.append(filters["date"])

    where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
    return fetch_all(
        f"""
        SELECT id, ip_address, port, protocol, username, status, alert, created_at
        FROM request_logs
        {where_clause}
        ORDER BY created_at DESC
        """,
        tuple(params),
    )


@logs_bp.route("/")
@login_required
def index():
    """Display searchable and filterable request history."""
    filters = _read_filters()
    return render_template(
        "logs.html",
        records=_filtered_logs(filters),
        filters=filters,
    )


@logs_bp.route("/export")
@login_required
def export_csv():
    """Download the currently filtered request logs as a CSV file."""
    records = _filtered_logs(_read_filters())
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["Request ID", "IP Address", "Port", "Protocol", "Username", "Status", "Alert", "Date & Time"]
    )
    for row in records:
        writer.writerow(
            [
                row["id"],
                row["ip_address"],
                row["port"],
                row["protocol"],
                row["username"] or "",
                row["status"],
                row["alert"],
                row["created_at"],
            ]
        )

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=request_logs.csv"},
    )
