import pandas as pd
from typing import Optional, Dict
from sqlalchemy import create_engine
from config import SQLITE_URL
from core.script_logger import audit_execution


@audit_execution("email_extractor")
def run_email_extractor(
    limit: int = 100,
    filters: Optional[Dict] = None
) -> Optional[pd.DataFrame]:
    """
    Extracción de correos por lotes.
    """

    engine = create_engine(SQLITE_URL)
    emails = []
    batch_size = 10

    while len(emails) < limit:
        batch = [
            {
                "entity_name": f"Email Subject {i}",
                "category": "Email",
                "value": 1.0
            }
            for i in range(batch_size)
        ]

        emails.extend(batch)

        if len(emails) >= limit:
            break

    df = pd.DataFrame(emails[:limit])

    if filters and "category" in filters:
        df = df[df["category"].isin(filters["category"])]

    if df.shape[0] == 0:
        return None

    df.to_sql("email_extraction_logs", engine, if_exists="replace", index=False)
    return df