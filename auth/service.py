import re
import bcrypt
from sqlalchemy import text

from auth.db import engine, init_users_table

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# --- PLAN DEFINITIONS (mock, no real billing yet) ---
PLAN_LIMITS = {
    "free": {
        "label": "Free",
        "sources": ["web", "api", "email"],
        "max_records": 50,
        "automation_rules": False,
    },
    "premium": {
        "label": "Premium",
        "sources": ["web", "api", "email", "excel", "pdf", "login"],
        "max_records": 10000,
        "automation_rules": True,
    },
}


def register_user(email: str, password: str) -> tuple[bool, str]:
    """Creates a new account on the Free plan. Returns (ok, message)."""
    email = email.strip().lower()

    if not EMAIL_PATTERN.match(email):
        return False, "That email address doesn't look valid."
    if len(password) < 6:
        return False, "Password must be at least 6 characters long."

    init_users_table()

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM users WHERE email = :email"), {"email": email}
        ).fetchone()
        if exists:
            return False, "An account with that email already exists."

        conn.execute(
            text("INSERT INTO users (email, password_hash, plan) VALUES (:email, :hash, 'free')"),
            {"email": email, "hash": password_hash},
        )

    return True, "Account created successfully. You can now log in."


def authenticate(email: str, password: str) -> tuple[bool, str]:
    """Verifies credentials. Returns (ok, message)."""
    email = email.strip().lower()
    init_users_table()

    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT password_hash FROM users WHERE email = :email"), {"email": email}
        ).fetchone()

    if not row:
        return False, "No account exists with that email."

    if not bcrypt.checkpw(password.encode("utf-8"), row[0].encode("utf-8")):
        return False, "Incorrect password."

    return True, "Logged in successfully."


def get_plan(email: str) -> str:
    email = email.strip().lower()
    init_users_table()

    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT plan FROM users WHERE email = :email"), {"email": email}
        ).fetchone()

    return row[0] if row else "free"


def set_plan(email: str, plan: str):
    """Changes the user's plan. This simulates an upgrade/downgrade: no real
    payment processor is connected yet, it's just a flag in the database."""
    if plan not in PLAN_LIMITS:
        raise ValueError(f"Unknown plan: {plan}")

    email = email.strip().lower()
    init_users_table()

    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET plan = :plan WHERE email = :email"),
            {"plan": plan, "email": email},
        )
