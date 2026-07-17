# Smart Network Firewall with Basic IDS Features

Academic simulation project for a Security Architecture course.

This application demonstrates:

- How a **firewall** blocks requests using IP and port rules
- How a basic **IDS** detects simple suspicious activities
- How request **logs** and **alerts** are stored in MySQL
- How an admin dashboard presents live statistics and charts

> Important: This is a **simulation only**. It does **not** sniff packets, change Windows/Linux firewall rules, or require administrator privileges.

---

## Features

| Module | Description |
|--------|-------------|
| Admin Login | Session-based login with a securely hashed password |
| Dashboard | Live counters, recent alerts, and Chart.js traffic charts |
| Firewall Management | Add, enable, disable, and remove IP or port rules |
| Request Simulator | Submit IP, port, protocol, username, and failed-login data |
| Logs | Search/filter request history and export matching rows to CSV |
| Alerts | Search alerts and filter by Low, Medium, High, or Critical severity |

### IDS Rules

1. Same IP makes **more than 5 requests within one minute**
2. A request matches an active **IP or port firewall rule**
3. **3 failed login attempts** (use the simulator checkbox)

---

## Project Structure

```text
se-project/
├── app.py                 # Small development entry point
├── config.py              # App + MySQL settings
├── requirements.txt       # Python dependencies
├── README.md
├── .env.example           # Example environment variables
├── database/
│   └── schema.sql         # MySQL database + tables
├── firewall_app/          # Modular Flask application package
│   ├── __init__.py        # Application factory
│   ├── auth/              # Admin login/logout
│   ├── main/              # Dashboard
│   ├── firewall/          # Rule management
│   ├── simulator/         # Request simulation
│   ├── logs/              # Search, filters, CSV
│   └── alerts/            # IDS alert views
├── static/
│   ├── css/style.css
│   └── js/main.js
├── templates/
│   ├── base.html
│   ├── auth/login.html
│   ├── dashboard.html
│   ├── firewall.html
│   ├── simulator.html
│   ├── logs.html
│   └── alerts.html
└── utils/
    ├── db.py              # MySQL helper functions
    ├── firewall.py        # Firewall simulation logic
    └── ids.py             # Basic IDS rules
```

---

## Requirements

- Python 3.10+ (3.8+ should also work)
- MySQL Server (XAMPP / WAMP / standalone MySQL)
- pip

---

## Setup Instructions

### 1) Create and activate a virtual environment (recommended)

**Windows (PowerShell):**

```powershell
cd path\to\se-project
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Windows (Command Prompt):**

```bat
cd path\to\se-project
python -m venv venv
venv\Scripts\activate.bat
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Create the MySQL database

1. Start MySQL (for example from XAMPP Control Panel).
2. Open MySQL Workbench, phpMyAdmin, or the MySQL terminal.
3. Run the file: `database/schema.sql`

This creates:

- database: `smart_firewall`
- tables: `admins`, `firewall_rules`, `request_logs`, `alerts`
- one sample IP firewall rule: `192.168.1.100`

If you already used the original version, starting the new app automatically
adds the new columns and tables without deleting your existing logs.

### 4) Configure database login

Either:

**Option A — edit `config.py`**

Set your MySQL password in:

```python
DB_PASSWORD = os.getenv("DB_PASSWORD", "your_password_here")
```

**Option B — use a `.env` file (recommended)**

```bash
copy .env.example .env
```

Then edit `.env`:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_NAME=smart_firewall
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
```

### 5) Run the application

```bash
python app.py
```

Open in your browser:

[http://127.0.0.1:5000](http://127.0.0.1:5000)

Default classroom login:

- Username: `admin`
- Password: `admin123`

Change these values in `.env` before sharing the project. They are used only
when the first admin account is created.

---

## How to Demonstrate

1. Sign in as the administrator and show the chart-based **Dashboard**.
2. Go to **Firewall Rules** and add an IP and a port rule.
3. Open **Simulator**:
   - Submit a normal IP → **Access Allowed**
   - Submit a blocked IP → **Access Denied** + IDS alert (Rule 2)
4. Submit the same IP more than 5 times quickly → IDS alert (Rule 1)
5. Check **Simulate failed login attempt** 3 times for one IP → IDS alert (Rule 3)
6. Search/filter **Logs**, export a CSV, and filter **Alerts** by severity.

---

## Technology Stack

- Backend: Python, Flask
- Frontend: HTML5, CSS3, Bootstrap 5, Chart.js, minimal JavaScript
- Database: MySQL (via PyMySQL)

---

## Notes for Presentation

- This project teaches **concepts**, not enterprise security.
- Firewall decisions use active IP and port rows in `firewall_rules`.
- IDS uses simple if/count rules — no machine learning.
- No Scapy, Wireshark, packet sniffing, or OS firewall changes are used.

---

## Troubleshooting

| Problem | Likely fix |
|---------|------------|
| Database connection failed | Start MySQL, run `schema.sql`, check password in `.env` / `config.py` |
| Module not found | Activate venv and run `pip install -r requirements.txt` |
| Port 5000 already in use | Stop the other app, or change `port=5000` in `app.py` |
| Page opens but tables empty | Run the Request Simulator to create sample data |

---

## License / Academic Use

Created for university coursework / demo purposes.
