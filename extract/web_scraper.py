import pandas as pd
from typing import Optional, Dict
from sqlalchemy import create_engine
from config import SQLITE_URL
from core.script_logger import audit_execution


@audit_execution("web_scraper")
def run_web_scraper(
    base_url: str,
    limit: int = 100,
    filters: Optional[Dict] = None
) -> Optional[pd.DataFrame]:
    """
    Scraper web simulado, consistente con el pipeline ETL.
    """

    engine = create_engine(SQLITE_URL)
    results = []
    page = 1

    while len(results) < limit:
        batch = [
            {
                "title": f"Web Item {i + (page - 1) * 10}",
                "category": "Web",
                "source": base_url,
                "value": float(i)
            }
            for i in range(10)
        ]

        results.extend(batch)
        page += 1

    df = pd.DataFrame(results[:limit])

    # Uso real de filters (evita warnings y errores lógicos)
    if filters and "category" in filters:
        df = df[df["category"].isin(filters["category"])]

    if df.empty:
        return None

    df.to_sql("raw_web_data", engine, if_exists="replace", index=False)
    return df