import pandas as pd
import numpy as np


class DataNormalizer:
    """
    Motor para la creación de columnas calculadas y transformaciones
    de estructura profesional.
    """

    @staticmethod
    def add_calculated_column(df: pd.DataFrame, name: str, formula: str) -> pd.DataFrame:
        """
        Punto 5: Crea columnas basadas en fórmulas matemáticas (ej: 'valor * 1.16').
        Utiliza evaluación segura de pandas.
        """
        try:
            # Aseguramos que el nombre no tenga espacios extra
            name = name.strip()
            # eval() ejecuta la operación sobre las columnas del dataframe
            df[name] = df.eval(formula)
            return df
        except Exception as e:
            raise ValueError(f"Error en la fórmula '{formula}': {e}")

    @staticmethod
    def split_column(df: pd.DataFrame, target_col: str, sep: str, new_names: list) -> pd.DataFrame:
        """
        Punto 7: Divide una columna en varias (ej: 'Nombre Apellido' -> 'Nombre', 'Apellido').
        """
        if target_col not in df.columns:
            return df

        # Realizamos el split
        split_data = df[target_col].astype(str).str.split(sep, expand=True)

        # Asignamos nombres a las nuevas columnas
        for i, name in enumerate(new_names):
            if i < len(split_data.columns):
                df[name.strip()] = split_data[i]

        return df

    @staticmethod
    def change_dtype(df: pd.DataFrame, column: str, new_type: str) -> pd.DataFrame:
        """
        Cambia el tipo de dato de una columna (Texto, Número, Fecha).
        """
        try:
            if new_type == "Número":
                df[column] = pd.to_numeric(df[column], errors='coerce')
            elif new_type == "Fecha":
                df[column] = pd.to_datetime(df[column], errors='coerce')
            elif new_type == "Texto":
                df[column] = df[column].astype(str)
            return df
        except Exception as e:
            raise ValueError(f"No se pudo convertir la columna {column}: {e}")