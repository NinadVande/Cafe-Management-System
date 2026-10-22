# Brew & Bean Cafe Management System

Flask and SQLite application for staff authentication, menu management, orders, and printable bills.

## Run on Windows PowerShell

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:SECRET_KEY = "replace-with-a-long-random-value"
python app.py
```

Open `http://127.0.0.1:5000`. The database initializes safely at `instance/cafe.sqlite`; existing data is retained. Without `SECRET_KEY`, a development-only fallback is used and must not be used in production.

Run tests with `python -m pytest -q`.

Main routes: `/register`, `/login`, `/menu`, `/menu/add`, `/order/create`, and `/orders`.
