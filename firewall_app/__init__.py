"""Application factory for the Smart Network Firewall project."""

from flask import Flask

from config import Config
from utils.db import ensure_database_schema


def create_app(config_class=Config):
    """Create and configure the Flask application."""
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_object(config_class)

    # Blueprints keep each feature in a small, easy-to-understand file.
    from firewall_app.auth.routes import auth_bp
    from firewall_app.main.routes import main_bp
    from firewall_app.firewall.routes import firewall_bp
    from firewall_app.simulator.routes import simulator_bp
    from firewall_app.logs.routes import logs_bp
    from firewall_app.alerts.routes import alerts_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(firewall_bp)
    app.register_blueprint(simulator_bp)
    app.register_blueprint(logs_bp)
    app.register_blueprint(alerts_bp)

    # Upgrade older project databases and create the first admin account.
    # This is idempotent: it is safe to run every time the app starts.
    with app.app_context():
        ensure_database_schema()

    return app
