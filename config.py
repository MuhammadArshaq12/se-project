"""
Application configuration settings.

Update DB_PASSWORD and other values to match your local MySQL setup.
You can also create a .env file (see .env.example) instead of editing this file.
"""

import os
from dotenv import load_dotenv

# Load variables from a .env file if it exists
load_dotenv()


class Config:
    """Flask and MySQL settings used by the whole application."""

    # Secret key used by Flask for session/flash messages
    SECRET_KEY = os.getenv("SECRET_KEY", "smart-firewall-student-project-key")

    # MySQL connection settings
    DB_HOST = os.getenv("DB_HOST", "localhost")
    DB_PORT = int(os.getenv("DB_PORT", "3306"))
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "smart_firewall")

    # A default admin is created automatically if the admins table is empty.
    # Change these values in .env before presenting or sharing the project.
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

    # Safer session-cookie defaults for a local development application.
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
