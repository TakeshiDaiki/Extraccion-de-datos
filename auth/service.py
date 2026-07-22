import hashlib
import re
import secrets
from datetime import datetime, timedelta

import bcrypt
from sqlalchemy import text

from auth.db import engine, init_users_table, init_remember_tokens_table

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
RECOVERY_KEY_ALPHABET = "23456789ABCDEFGHJKLMNPQRSTUVWXYZ"  # no 0/O/1/I/L, avoids ambiguous chars
RECOVERY_KEY_GROUPS = 4
RECOVERY_KEY_GROUP_LEN = 4

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


def _generate_recovery_key() -> str:
    """A random human-writable recovery key, e.g. 'K7F2-9RTX-M4WQ-2ZPY'.
    This is the account's only path back in if the password is lost —
    there's no email step, so losing it means losing the account."""
    groups = [
        "".join(secrets.choice(RECOVERY_KEY_ALPHABET) for _ in range(RECOVERY_KEY_GROUP_LEN))
        for _ in range(RECOVERY_KEY_GROUPS)
    ]
    return "-".join(groups)


def register_user(email: str, password: str) -> tuple[bool, str, str | None]:
    """Creates a new account on the Free plan and a one-time recovery key
    (shown to the user once, never stored in plaintext). Returns
    (ok, message, recovery_key) — recovery_key is None on failure."""
    email = email.strip().lower()

    if not EMAIL_PATTERN.match(email):
        return False, "That email address doesn't look valid.", None
    if len(password) < 6:
        return False, "Password must be at least 6 characters long.", None

    init_users_table()

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    recovery_key = _generate_recovery_key()
    recovery_key_hash = bcrypt.hashpw(recovery_key.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM users WHERE email = :email"), {"email": email}
        ).fetchone()
        if exists:
            return False, "An account with that email already exists.", None

        conn.execute(
            text(
                "INSERT INTO users (email, password_hash, plan, recovery_key_hash) "
                "VALUES (:email, :hash, 'free', :recovery_hash)"
            ),
            {"email": email, "hash": password_hash, "recovery_hash": recovery_key_hash},
        )

    return True, "Account created successfully. You can now log in.", recovery_key


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


def reset_password_with_recovery_key(email: str, recovery_key: str, new_password: str) -> tuple[bool, str]:
    """Replaces the account's password if recovery_key matches the one
    generated at registration. No email step involved — the key itself is
    the credential, so it stays valid indefinitely (not single-use)."""
    email = email.strip().lower()
    recovery_key = recovery_key.strip().upper()
    if len(new_password) < 6:
        return False, "Password must be at least 6 characters long."

    init_users_table()

    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT recovery_key_hash FROM users WHERE email = :email"), {"email": email}
        ).fetchone()

    if not row or not row[0]:
        return False, "No account with a recovery key exists for that email."

    if not bcrypt.checkpw(recovery_key.encode("utf-8"), row[0].encode("utf-8")):
        return False, "That recovery key doesn't match this account."

    new_hash = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET password_hash = :hash WHERE email = :email"),
            {"hash": new_hash, "email": email},
        )

    return True, "Password updated. You can now log in with your new password."


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def create_remember_token(email: str, days: int) -> str:
    """Issues a new "remember me" token for a "Remember me"-checked login and
    stores only its hash, alongside its expiry. Returns the raw token — the
    caller is responsible for handing it to the browser as a cookie."""
    email = email.strip().lower()
    init_remember_tokens_table()

    token = secrets.token_urlsafe(32)
    expires_at = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d %H:%M:%S")

    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO remember_tokens (token_hash, email, expires_at) VALUES (:hash, :email, :expires_at)"),
            {"hash": _hash_token(token), "email": email, "expires_at": expires_at},
        )

    return token


def verify_remember_token(token: str) -> str | None:
    """Returns the associated email if the token is valid and unexpired,
    else None."""
    if not token:
        return None
    init_remember_tokens_table()

    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT email FROM remember_tokens "
                "WHERE token_hash = :hash AND expires_at > CURRENT_TIMESTAMP"
            ),
            {"hash": _hash_token(token)},
        ).fetchone()

    return row[0] if row else None


def revoke_remember_token(token: str) -> None:
    """Invalidates a "remember me" token, e.g. on logout."""
    if not token:
        return
    init_remember_tokens_table()

    with engine.begin() as conn:
        conn.execute(text("DELETE FROM remember_tokens WHERE token_hash = :hash"), {"hash": _hash_token(token)})
