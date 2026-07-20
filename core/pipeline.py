import sys
import logging
import pandas as pd

# Evita UnicodeEncodeError con emojis cuando el proceso que importa este
# módulo (API, dashboard, scheduler, run_all.py) corre en una consola
# Windows que no usa UTF-8 por defecto.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
from extract.web_scraper import run_web_scraper
from extract.api_client import fetch_external_api
from extract.login_scraper import run_login_scraper
from extract.email_extractor import run_email_extractor
from extract.excel_extractor import run_excel_extraction
from extract.pdf_reader import run_pdf_extraction
from core.filter_engine import apply_filters
from core.pipeline_manager import PipelineManager  # <--- Nueva integración
from config import CONFIG


def run_pipeline(
        sources: list,
        limit: int = 100,
        filters: dict | None = None,
        user_inputs: dict | None = None
):
    """
    Orquestador Maestro con Capa de Automatización ETL.
    """
    results = {"success": [], "errors": [], "counts": {}}
    active_config = {**CONFIG, **(user_inputs or {})}

    # Mapeo de fuentes a tablas de la base de datos
    db_table_map = {
        "web": "raw_web_data",
        "api": "raw_api_data",
        "login": "raw_login_data",
        "email": "email_extraction_logs",
        "excel": "raw_excel_data",
        "pdf": "raw_pdf_data"
    }

    engine_map = {
        "web": (run_web_scraper, {"base_url": active_config.get("SCRAPER_URL")}),
        "api": (fetch_external_api, {"api_endpoint": active_config.get("API_BASE_URL")}),
        "login": (run_login_scraper, {"url": active_config.get("LOGIN_URL")}),
        "email": (run_email_extractor, {}),
        "excel": (run_excel_extraction, {}),
        "pdf": (run_pdf_extraction, {})
    }

    for source in sources:
        if source in engine_map:
            func, kwargs = engine_map[source]
            try:
                # 1. EXTRACCIÓN
                raw_df = func(limit=limit, filters=filters, **kwargs)

                if isinstance(raw_df, pd.DataFrame):
                    # 2. FILTRADO INICIAL (Capa técnica)
                    df = apply_filters(raw_df, filters)

                    # 3. AUTOMATIZACIÓN ETL (Capa Profesional - Punto 11)
                    # Aplica reglas guardadas por el usuario en el Dashboard
                    table_name = db_table_map.get(source)
                    df = PipelineManager.apply_stored_rules(table_name, df)

                    final_count = len(df)
                else:
                    final_count = raw_df or 0

                results["success"].append(source)
                results["counts"][source] = final_count
                print(f"✅ {source.upper()}: {final_count} registros procesados con éxito.")

            except Exception as e:
                logging.error(f"Error en {source}: {str(e)}")
                results["errors"].append({"source": source, "error": str(e)})

    return results