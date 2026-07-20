# assistant/command_router.py
from extract.web_scraper import run_web_scraper
from extract.login_scraper import run_login_scraper
from extract.api_client import fetch_external_api
from extract.email_extractor import run_email_extractor
from extract.pdf_reader import run_pdf_extraction
from extract.excel_extractor import run_excel_extraction
from core.pipeline import run_pipeline
from config import CONFIG


def route_command(option_num, limit, url=None):
    """
    Enruta las instrucciones recibidas desde la interfaz de Streamlit
    hacia los motores de extracción correspondientes.
    """
    # 1. Web Scraping
    if option_num == "1":
        return run_web_scraper(base_url=url, limit=limit)

    # 2. Login Scraping
    elif option_num == "2":
        return run_login_scraper(url=url, limit=limit)

    # 3. API Extraction
    elif option_num == "3":
        api_endpoint = url or CONFIG.get("API_BASE_URL", "")
        return fetch_external_api(api_endpoint=api_endpoint, limit=limit)

    # 4. Email Extraction
    elif option_num == "4":
        return run_email_extractor(limit=limit)

    # 5. PDF Processing
    elif option_num == "5":
        return run_pdf_extraction(limit=limit)

    # 6. Excel Processing
    elif option_num == "6":
        return run_excel_extraction(limit=limit)

    # 7. Ejecutar Pipeline Completo
    elif option_num == "7":
        all_sources = ['web', 'api', 'email', 'pdf', 'excel', 'login']
        return run_pipeline(sources=all_sources, limit=limit)

    return None