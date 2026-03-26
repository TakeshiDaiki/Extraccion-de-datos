import pandas as pd


class Deduplicator:
    """Handles data redundancy con lógica avanzada"""

    @staticmethod
    def remove_duplicates(df: pd.DataFrame, column: str = None, keep: str = 'first') -> pd.DataFrame:
        """
        Removes duplicate rows based on a column or entire row.
        keep: 'first' (mantiene el primer registro encontrado), 'last' (el último).
        """
        if column and column in df.columns:
            # Deduplicación inteligente por columna específica
            return df.drop_duplicates(subset=[column], keep=keep).reset_index(drop=True)

        # Deduplicación estándar de toda la fila
        return df.drop_duplicates(keep=keep).reset_index(drop=True)