"""Development entry point for the Smart Network Firewall project."""

from firewall_app import create_app

# The application factory lives in firewall_app/__init__.py.
# Keeping this file tiny makes the project easier to test and extend.
app = create_app()


if __name__ == "__main__":
    app.run(debug=True, host="127.0.0.1", port=5000)
