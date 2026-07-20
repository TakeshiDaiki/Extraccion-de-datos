from sqlalchemy import create_engine, text

from config import SQLITE_URL

engine = create_engine(SQLITE_URL)


def init_users_table():
    """Crea la tabla de usuarios si todavía no existe. Se apoya en la misma
    base de datos compartida por el resto del sistema (config.SQLITE_URL)."""
    with engine.begin() as conn:
        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                plan TEXT NOT NULL DEFAULT 'free',
                paypal_subscription_id TEXT,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
        existing_cols = {row[1] for row in conn.execute(text("PRAGMA table_info(users)"))}
        if "paypal_subscription_id" not in existing_cols:
            conn.execute(text("ALTER TABLE users ADD COLUMN paypal_subscription_id TEXT"))

        conn.execute(text("""
            CREATE TABLE IF NOT EXISTS password_reset_codes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT NOT NULL,
                code_hash TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                used INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
