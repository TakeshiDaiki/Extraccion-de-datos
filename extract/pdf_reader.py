import os
import pandas as pd
from typing import Optional, Dict
from sqlalchemy import create_engine
from config import SQLITE_URL, DATA_INPUT_DIR
from core.script_logger import audit_execution


@audit_execution("pdf_reader")
def run_pdf_extraction(
    limit: int = 100,
    filters: Optional[Dict] = None
) -> Optional[pd.DataFrame]:
    """
    Lectura básica de PDFs por páginas (simulado).
    """

    engine = create_engine(SQLITE_URL)
    records = []

    for file in os.listdir(DATA_INPUT_DIR):
        if not file.lower().endswith(".pdf"):
            continue

        records.append({
            "entity_name": f"PDF content from {file}",
            "category": "PDF",
            "value": 5.5
        })

        if len(records) >= limit:
            break

    df = pd.DataFrame(records)

    if filters and "category" in filters:
        df = df[df["category"].isin(filters["category"])]

    if df.shape[0] == 0:
        return None

    df.to_sql("raw_pdf_data", engine, if_exists="replace", index=False)
    return df