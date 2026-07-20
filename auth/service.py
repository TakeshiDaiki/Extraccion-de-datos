import re
import bcrypt
from sqlalchemy import text

from auth.db import engine, init_users_table

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

# --- DEFINICIÓN DE PLANES (maqueta, no hay cobro real) ---
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
    """Crea una cuenta nueva en plan Free. Devuelve (ok, mensaje)."""
    email = email.strip().lower()

    if not EMAIL_PATTERN.match(email):
        return False, "El email no tiene un formato válido."
    if len(password) < 6:
        return False, "La contraseña debe tener al menos 6 caracteres."

    init_users_table()

    password_hash = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    with engine.begin() as conn:
        exists = conn.execute(
            text("SELECT 1 FROM users WHERE email = :email"), {"email": email}
        ).fetchone()
        if exists:
            return False, "Ya existe una cuenta registrada con ese email."

        conn.execute(
            text("INSERT INTO users (email, password_hash, plan) VALUES (:email, :hash, 'free')"),
            {"email": email, "hash": password_hash},
        )

    return True, "Cuenta creada con éxito. Ya podés iniciar sesión."


def authenticate(email: str, password: str) -> tuple[bool, str]:
    """Verifica credenciales. Devuelve (ok, mensaje)."""
    email = email.strip().lower()
    init_users_table()

    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT password_hash FROM users WHERE email = :email"), {"email": email}
        ).fetchone()

    if not row:
        return False, "No existe una cuenta con ese email."

    if not bcrypt.checkpw(password.encode("utf-8"), row[0].encode("utf-8")):
        return False, "Contraseña incorrecta."

    return True, "Login correcto."


def get_plan(email: str) -> str:
    email = email.strip().lower()
    init_users_table()

    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT plan FROM users WHERE email = :email"), {"email": email}
        ).fetchone()

    return row[0] if row else "free"


def set_plan(email: str, plan: str):
    """Cambia el plan del usuario. Simulación de upgrade/downgrade: no hay
    ningún procesador de pagos conectado, es solo un flag en la base de datos."""
    if plan not in PLAN_LIMITS:
        raise ValueError(f"Plan desconocido: {plan}")

    email = email.strip().lower()
    init_users_table()

    with engine.begin() as conn:
        conn.execute(
            text("UPDATE users SET plan = :plan WHERE email = :email"),
            {"plan": plan, "email": email},
        )
