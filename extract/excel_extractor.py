import os
import pandas as pd
from typing import Optional, Dict
from sqlalchemy import create_engine
from config import SQLITE_URL, DATA_INPUT_DIR
from core.script_logger import audit_execution


@audit_execution("excel_extractor")
def run_excel_extraction(
    limit: int = 100,
    filters: Optional[Dict] = None
) -> Optional[pd.DataFrame]:
    """
    Extracción segura desde archivos Excel.
    """

    engine = create_engine(SQLITE_URL)
    dataframes: list[pd.DataFrame] = []

    for file in os.listdir(DATA_INPUT_DIR):
        if not file.lower().endswith((".xlsx", ".xls")):
            continue

        path = os.path.join(DATA_INPUT_DIR, file)

        try:
            df_file = pd.read_excel(path)

            if df_file.shape[0] == 0:
                continue

            dataframes.append(df_file)

        except Exception as exc:
            print(f"⚠️ Error leyendo {file}: {exc}")

    if len(dataframes) == 0:
        return None

    # ⬇️ Forzamos tipo explícito (elimina el warning 'Never')
    df: pd.DataFrame = pd.concat(dataframes, ignore_index=True)
    df = df.head(limit)

    if filters and "category" in df.columns:
        df = df[df["category"].isin(filters["category"])]

    if df.shape[0] == 0:
        return None

    df.to_sql("raw_excel_data", engine, if_exists="replace", index=False)
    return df