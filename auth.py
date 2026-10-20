import re
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash
from database import get_db

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def get_user_by_email(email):
    return get_db().execute("SELECT * FROM users WHERE email = ?", (email.lower(),)).fetchone()

def validate_registration(name, email, password, confirm):
    if not all((name, email, password, confirm)): return "All fields are required."
    if not EMAIL_RE.match(email): return "Enter a valid email address."
    if len(password) < 8 or not any(c.isalpha() for c in password) or not any(c.isdigit() for c in password): return "Password must be at least 8 characters and include a letter and number."
    if password != confirm: return "Passwords do not match."

def create_user(full_name, email, password):
    try:
        db = get_db(); db.execute("INSERT INTO users (full_name, email, password_hash) VALUES (?, ?, ?)", (full_name, email.lower(), generate_password_hash(password))); db.commit(); return True
    except sqlite3.IntegrityError:
        get_db().rollback(); return False

def verify_user_password(email, password):
    user = get_user_by_email(email)
    return bool(user and check_password_hash(user["password_hash"], password))
