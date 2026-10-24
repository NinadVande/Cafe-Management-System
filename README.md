# Cafe Management System

A web-based cafe management application built with **Python, Flask, SQLite, HTML, CSS, and JavaScript** to manage menu items, user authentication, orders, and billing.

## Features

- **Menu Management** — Add, view, search, edit, and delete menu items.
- **User Authentication** — Registration, login, logout, and password hashing.
- **Order Management** — Create orders and maintain order history.
- **Billing** — Calculate order totals and preserve item prices in order records.
- **Testing** — Automated tests using `pytest`.

## Tech Stack

- **Backend:** Python, Flask
- **Database:** SQLite
- **Frontend:** HTML, CSS, JavaScript
- **Testing:** pytest

## Getting Started

1. Clone the repository:

   ```bash
   git clone https://github.com/NinadVande/Cafe-Management-System.git
   cd Cafe-Management-System
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   ```

   Windows PowerShell:

   ```powershell
   .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install Flask pytest Werkzeug
   ```

4. Run the application:

   ```bash
   python app.py
   ```

5. Open the local URL shown in the terminal.

## Run Tests

```bash
python -m pytest -v
```

## Project Status

Developed as a **Problem-Based Learning (PBL)** project.