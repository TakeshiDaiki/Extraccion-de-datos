import pandas as pd

def apply_filters(df: pd.DataFrame, filters: dict | None) -> pd.DataFrame:
    """
    Motor de filtrado inteligente.
    Aplica filtros de categoría, rango numérico y palabras clave al dataset extraído.
    """

    if df.empty or not filters:
        return df

    # Asegurar que la columna 'value' sea numérica antes de filtrar
    if 'value' in df.columns:
        df['value'] = pd.to_numeric(df['value'], errors='coerce')

    # 1. Filtro de Categorías (Sección 8.2 del informe)
    if "categories" in filters and "category" in df.columns:
        # Filtra solo si las categorías coinciden con la lista permitida
        df = df[df["category"].isin(filters["categories"])]

    # 2. Filtros de Rango Numérico (KPI Validation)
    if "min_value" in filters and "value" in df.columns:
        df = df[df["value"] >= filters["min_value"]]

    if "max_value" in filters and "value" in df.columns:
        df = df[df["value"] <= filters["max_value"]]

    # 3. Filtro de Palabras Clave (Entity Recognition simple)
    if "keywords" in filters and "entity_name" in df.columns:
        # Crea un patrón regex para buscar múltiples palabras clave
        pattern = "|".join(filters["keywords"])
        df = df[df["entity_name"].str.contains(pattern, case=False, na=False)]

    return df