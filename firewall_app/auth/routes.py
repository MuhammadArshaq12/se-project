"""Admin login and logout routes."""

from functools import wraps

from flask import (
    Blueprint,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash

from utils.db import fetch_one

auth_bp = Blueprint("auth", __name__)


def login_required(view_function):
    """Redirect visitors to login before they access admin pages."""

    @wraps(view_function)
    def wrapped_view(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please sign in to access the admin panel.", "warning")
            return redirect(url_for("auth.login", next=request.path))
        return view_function(*args, **kwargs)

    return wrapped_view


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Authenticate an administrator with a hashed password."""
    if "admin_id" in session:
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        admin = fetch_one(
            "SELECT id, username, password_hash FROM admins WHERE username = %s",
            (username,),
        )

        if admin and check_password_hash(admin["password_hash"], password):
            session.clear()
            session["admin_id"] = admin["id"]
            session["admin_username"] = admin["username"]
            flash("Welcome back. You are now signed in.", "success")

            # Only allow an internal path as the post-login destination.
            next_page = request.args.get("next", "")
            if next_page.startswith("/") and not next_page.startswith("//"):
                return redirect(next_page)
            return redirect(url_for("main.dashboard"))

        flash("Invalid username or password.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/logout")
def logout():
    """End the current admin session."""
    session.clear()
    flash("You have been signed out.", "info")
    return redirect(url_for("auth.login"))
