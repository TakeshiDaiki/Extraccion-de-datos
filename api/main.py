import os
import pandas as pd
from datetime import datetime
from sqlalchemy import create_engine

from core.script_logger import audit_execution

# ==========================================================
# SETTINGS
# ==========================================================

SCRIPT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATABASE_TARGET = os.path.join(SCRIPT_ROOT, "dashboards", "etl_pro.db")


@audit_execution("main_etl")
def run_data_injection():
    """
    Main ETL injection logic.
    Generates operational data and persists it into SQLite.
    """

    print(f"[{datetime.now()}] Initializing Production Data Injection")

    os.makedirs(os.path.dirname(DATABASE_TARGET), exist_ok=True)

    data_payload = pd.DataFrame({
        "date": pd.date_range(start="2026-02-16", periods=100),
        "value": [v * 75.5 for v in range(100)],
        "status": ["OPERATIONAL_LIVE"] * 100
    })

    engine = create_engine(f"sqlite:///{DATABASE_TARGET}")
    data_payload.to_sql(
        "processed_data",
        engine,
        if_exists="append",
        index=False
    )

    print("✅ Injection completed successfully")


if __name__ == "__main__":
    run_data_injection()