from sqlalchemy import create_engine
import pandas as pd

class DatabaseManager:
    """Handles SQLite persistence."""
    def __init__(self, db_name="etl_pro.db"):
        self.engine = create_engine(f'sqlite:///{db_name}')

    def save_data(self, df: pd.DataFrame, table_name: str):
        df.to_sql(table_name, self.engine, if_exists='replace', index=False)