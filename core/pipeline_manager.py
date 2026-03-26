import json
import os
import pandas as pd
from transform.cleaner import DataCleaner
from transform.normalizer import DataNormalizer
from transform.deduplicator import Deduplicator


class PipelineManager:
    """Gestiona la persistencia y ejecución de flujos ETL"""

    RULES_PATH = os.path.join("config", "pipeline_rules.json")

    @classmethod
    def apply_stored_rules(cls, table_name: str, df: pd.DataFrame) -> pd.DataFrame:
        """Aplica automáticamente la secuencia de limpieza guardada para una fuente"""
        rules = cls._load_rules().get(table_name, [])

        for rule in rules:
            action = rule['action']
            params = rule.get('params', {})

            try:
                if action == "DEDUPLICATE":
                    df = Deduplicator.remove_duplicates(df, column=params.get('column'))
                elif action == "CLEAN_TEXT":
                    df = DataCleaner.trim_spaces(df)
                elif action == "NEW_COLUMN":
                    df = DataNormalizer.add_calculated_column(df, params['name'], params['formula'])
            except Exception as e:
                print(f"⚠️ Error aplicando regla {action} en {table_name}: {e}")

        return df

    @classmethod
    def _load_rules(cls):
        if os.path.exists(cls.RULES_PATH):
            with open(cls.RULES_PATH, "r") as f:
                return json.load(f)
        return {}