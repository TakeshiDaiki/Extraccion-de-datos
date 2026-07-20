from sqlalchemy import create_engine
import pandas as pd

from config import SQLITE_URL

class DatabaseManager:
    """Handles SQLite persistence. Apunta a la misma base de datos que usa
    el resto del pipeline (config.SQLITE_URL) para evitar bases de datos
    huérfanas/desincronizadas."""
    def __init__(self, db_url: str = SQLITE_URL):
        self.engine = create_engine(db_url)

    def save_data(self, df: pd.DataFrame, table_name: str):
        df.to_sql(table_name, self.engine, if_exists='replace', index=False)