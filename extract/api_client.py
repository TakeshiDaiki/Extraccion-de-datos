import pandas as pd
from typing import Optional, Dict
from sqlalchemy import create_engine
from config import SQLITE_URL
from core.script_logger import audit_execution


@audit_execution("api_client")
def fetch_external_api(
    api_endpoint: str,
    limit: int = 100,
    filters: Optional[Dict] = None
) -> Optional[pd.DataFrame]:
    """
    Cliente de API externo.
    La firma es 100% compatible con core.pipeline.
    """

    engine = create_engine(SQLITE_URL)

    # Simulación de datos API (estable, reproducible)
    data = [
        {
            "id": i,
            "name": f"API Item {i}",
            "source": api_endpoint,
            "value": float(i * 10)
        }
        for i in range(limit)
    ]

    df = pd.DataFrame(data)

    # Uso real de filters (evita warnings y errores)
    if filters and "min_value" in filters:
        df = df[df["value"] >= filters["min_value"]]

    if df.empty:
        return None

    df.to_sql("raw_api_data", engine, if_exists="replace", index=False)
    return df