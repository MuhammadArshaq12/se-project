"""Firewall rule management routes."""

import ipaddress

from flask import Blueprint, flash, redirect, render_template, request, url_for

from firewall_app.auth.routes import login_required
from utils.firewall import add_rule, delete_rule, get_rules, toggle_rule

firewall_bp = Blueprint("firewall", __name__, url_prefix="/firewall")


@firewall_bp.route("/")
@login_required
def index():
    """List all IP and port rules."""
    return render_template("firewall.html", rules=get_rules())


@firewall_bp.route("/add", methods=["POST"])
@login_required
def add():
    """Validate and add a simulated firewall rule."""
    rule_type = request.form.get("rule_type", "").upper()
    value = request.form.get("value", "").strip()
    description = request.form.get("description", "").strip()

    if rule_type not in {"IP", "PORT"}:
        flash("Please select IP Address or Port Number.", "warning")
        return redirect(url_for("firewall.index"))

    try:
        if rule_type == "IP":
            value = str(ipaddress.ip_address(value))
        else:
            port = int(value)
            if not 1 <= port <= 65535:
                raise ValueError
            value = str(port)
    except ValueError:
        label = "a valid IPv4/IPv6 address" if rule_type == "IP" else "a port from 1 to 65535"
        flash(f"Please enter {label}.", "warning")
        return redirect(url_for("firewall.index"))

    success, message = add_rule(rule_type, value, description)
    flash(message, "success" if success else "warning")
    return redirect(url_for("firewall.index"))


@firewall_bp.route("/<int:rule_id>/toggle", methods=["POST"])
@login_required
def toggle(rule_id):
    """Enable or disable a rule without deleting it."""
    success, message = toggle_rule(rule_id)
    flash(message, "success" if success else "warning")
    return redirect(url_for("firewall.index"))


@firewall_bp.route("/<int:rule_id>/delete", methods=["POST"])
@login_required
def delete(rule_id):
    """Permanently delete one rule."""
    success, message = delete_rule(rule_id)
    flash(message, "success" if success else "warning")
    return redirect(url_for("firewall.index"))
