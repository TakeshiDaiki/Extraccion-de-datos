import pandas as pd
from typing import Optional, Dict
from sqlalchemy import create_engine
from config import SQLITE_URL
from core.script_logger import audit_execution


@audit_execution("login_scraper")
def run_login_scraper(
    url: str,
    limit: int = 100,
    filters: Optional[Dict] = None
) -> Optional[pd.DataFrame]:
    """
    Scraper autenticado (simulado).
    """

    engine = create_engine(SQLITE_URL)
    results = []
    offset = 0
    batch_size = 25

    while len(results) < limit:
        batch = [
            {
                "entity_name": f"Secure Data {i + offset}",
                "category": "Login",
                "source": url,
                "value": 50.0
            }
            for i in range(batch_size)
        ]

        results.extend(batch)
        offset += batch_size

    df = pd.DataFrame(results[:limit])

    # ⬇️ Uso explícito de filters (elimina warning)
    if filters and "category" in filters:
        df = df[df["category"].isin(filters["category"])]

    if df.shape[0] == 0:
        return None

    df.to_sql("raw_login_data", engine, if_exists="replace", index=False)
    return df