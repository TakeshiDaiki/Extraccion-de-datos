import re
import secrets
from datetime import datetime, timedelta, timezone

import bcrypt
from sqlalchemy import text

from auth.db import engine, init_users_table
from notifications.sendgrid_service import send_reset_code

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
RESET_CODE_TTL_MINUTES = 15

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


def set_plan(email: str, plan: str, subscription_id: str | None = None):
    """Changes the user's plan. When upgrading to Premium via a real PayPal
    subscription, pass the resulting subscription_id so it can be canceled
    later on downgrade. Downgrading to Free always clears it."""
    if plan not in PLAN_LIMITS:
        raise ValueError(f"Unknown plan: {plan}")

    email = email.strip().lower()
    init_users_table()

    with engine.begin() as conn:
        if plan == "free":
            conn.execute(
                text("UPDATE users SET plan = :plan, paypal_subscription_id = NULL WHERE email = :email"),
                {"plan": plan, "email": email},
            )
        else:
            conn.execute(
                text(
                    "UPDATE users SET plan = :plan, "
                    "paypal_subscription_id = COALESCE(:sub_id, paypal_subscription_id) "
                    "WHERE email = :email"
                ),
                {"plan": plan, "email": email, "sub_id": subscription_id},
            )


def get_subscription_id(email: str) -> str | None:
    email = email.strip().lower()
    init_users_table()

    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT paypal_subscription_id FROM users WHERE email = :email"), {"email": email}
        ).fetchone()

    return row[0] if row and row[0] else None


def request_password_reset(email: str) -> tuple[bool, str]:
    """Generates a 6-digit reset code, emails it via SendGrid, and stores
    only its bcrypt hash (never the plaintext code) with a 15-minute
    expiry. Returns (ok, message)."""
    email = email.strip().lower()
    init_users_table()

    with engine.connect() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM users WHERE email = :email"), {"email": email}
        ).fetchone()
    if not exists:
        return False, "No account exists with that email."

    code = f"{secrets.randbelow(1_000_000):06d}"
    code_hash = bcrypt.hashpw(code.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    expires_at = (datetime.now(timezone.utc) + timedelta(minutes=RESET_CODE_TTL_MINUTES)).isoformat()

    sent_ok, sent_message = send_reset_code(email, code)
    if not sent_ok:
        return False, sent_message

    with engine.begin() as conn:
        # Invalidate any codes still pending from earlier requests so only
        # the one just emailed can be used.
        conn.execute(
            text("UPDATE password_reset_codes SET used = 1 WHERE email = :email AND used = 0"),
            {"email": email},
        )
        conn.execute(
            text(
                "INSERT INTO password_reset_codes (email, code_hash, expires_at) "
                "VALUES (:email, :hash, :expires_at)"
            ),
            {"email": email, "hash": code_hash, "expires_at": expires_at},
        )

    return True, f"A reset code was sent to {email}. It expires in {RESET_CODE_TTL_MINUTES} minutes."


def reset_password(email: str, code: str, new_password: str) -> tuple[bool, str]:
    """Verifies a reset code emailed by request_password_reset() and, if
    valid and unexpired, replaces the account's password. Returns (ok, message)."""
    email = email.strip().lower()
    if len(new_password) < 6:
        return False, "Password must be at least 6 characters long."

    init_users_table()

    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT id, code_hash, expires_at FROM password_reset_codes "
                "WHERE email = :email AND used = 0 ORDER BY id DESC LIMIT 1"
            ),
            {"email": email},
        ).fetchone()

    if not row:
        return False, "No pending reset code for this email. Request a new one."

    reset_id, code_hash, expires_at = row
    if datetime.now(timezone.utc) > datetime.fromisoformat(expires_at):
        return False, "This reset code has expired. Request a new one."

    if not bcrypt.checkpw(code.encode("utf-8"), code_hash.encode("utf-8")):
        return False, "Incorrect reset code."

    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET password_hash = :hash WHERE email = :email"),
            {"hash": new_hash, "email": email},
        )
        conn.execute(
            text("UPDATE password_reset_codes SET used = 1 WHERE id = :id"),
            {"id": reset_id},
        )

    return True, "Password updated. You can now log in with your new password."
