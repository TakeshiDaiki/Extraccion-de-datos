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
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """))
