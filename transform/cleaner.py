import pandas as pd


class DataCleaner:
    """Motor de limpieza avanzada y perfilado de datos"""

    @staticmethod
    def get_column_health(df: pd.DataFrame) -> pd.DataFrame:
        """Punto 8: Perfilado de salud de las columnas"""
        stats = []
        for col in df.columns:
            nulls = df[col].isnull().sum()
            stats.append({
                "Columna": col,
                "Tipo": str(df[col].dtype),
                "Nulos": nulls,
                "% Salud": round(((len(df) - nulls) / len(df)) * 100, 2) if len(df) > 0 else 0,
                "Únicos": df[col].nunique()
            })
        return pd.DataFrame(stats)

    @staticmethod
    def advanced_text_process(df: pd.DataFrame, column: str, mode: str) -> pd.DataFrame:
        """
        Punto 4: Procesamiento semántico de texto.
        Modos: UPPER, LOWER, TITLE, STRIP_ACCENTS
        """
        if column in df.columns:
            # Aseguramos que sea string antes de operar
            series = df[column].astype(str)

            if mode == "UPPER":
                df[column] = series.str.upper()
            elif mode == "LOWER":
                df[column] = series.str.lower()
            elif mode == "TITLE":
                df[column] = series.str.title()
            elif mode == "STRIP_ACCENTS":
                # Normalización Unicode para eliminar tildes y caracteres especiales
                df[column] = series.str.normalize('NFKD').str.encode('ascii', 'ignore').str.decode('utf-8')
        return df

    @staticmethod
    def mass_replace(df: pd.DataFrame, column: str, to_replace: str, value: str) -> pd.DataFrame:
        """Punto 4: Búsqueda y reemplazo masivo en una columna específica"""
        if column in df.columns:
            df[column] = df[column].replace(to_replace, value)
        return df

    @staticmethod
    def purge_empty_rows(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
        """
        Elimina filas que tengan más de un porcentaje de nulos definido.
        Ejemplo: threshold=0.5 elimina filas con más del 50% de columnas vacías.
        """
        limit = int((1 - threshold) * len(df.columns))
        return df.dropna(thresh=limit).reset_index(drop=True)

    @staticmethod
    def trim_spaces(df: pd.DataFrame) -> pd.DataFrame:
        """Elimina espacios en blanco al inicio y final en todas las celdas de texto"""
        str_cols = df.select_dtypes(include=['object']).columns
        for col in str_cols:
            df[col] = df[col].astype(str).str.strip()
        return df

    @staticmethod
    def normalize_headers(df: pd.DataFrame) -> pd.DataFrame:
        """Convierte los nombres de columnas a snake_case profesional"""
        df.columns = [col.strip().lower().replace(" ", "_").replace(".", "_") for col in df.columns]
        return df