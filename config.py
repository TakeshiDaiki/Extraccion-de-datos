import os

# --- 1. RUTAS DEL SISTEMA ---
# Definimos la ruta base para asegurar portabilidad en cualquier carpeta
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_INPUT_DIR = os.path.join(BASE_DIR, "data_input")
PROCESSED_DIR = os.path.join(BASE_DIR, "data_processed")
DATABASE_PATH = os.path.join(BASE_DIR, "database.db")

# URL de conexión para SQLAlchemy
SQLITE_URL = f"sqlite:///{DATABASE_PATH}"

# --- 2. CONFIGURACIÓN DINÁMICA (Valores por defecto) ---
# Estos valores serán sobreescritos por lo que ingreses en el Dashboard
CONFIG = {
    "EMAIL_USER": "",
    "EMAIL_PASS": "",
    "SCRAPER_URL": "", # Valor sugerido inicial
    "API_BASE_URL": "",
    "LOGIN_URL": ""
}

# --- 3. ESQUEMAS DE BASE DE DATOS ---
# Definimos el contrato de datos para que todos los motores guarden lo mismo
DATABASE_SCHEMAS = {
    "raw_web_data": ["entity_name", "category", "value", "currency", "rating", "stock_status", "product_url", "scraped_at"],
    "raw_api_data": ["id", "source", "payload", "synced_at"],
    "email_extraction_logs": ["sender", "subject", "date_received", "body_preview"],
    "raw_login_data": ["user_id", "session_token", "last_login"],
    "raw_pdf_data": ["entity_name", "category", "value", "extracted_at"],
    "raw_excel_data": ["entity_name", "category", "value", "extracted_at"]
}

# --- 4. INICIALIZACIÓN DE ENTORNO ---
# Creamos las carpetas necesarias si no existen para evitar errores de IO
for folder in [DATA_INPUT_DIR, PROCESSED_DIR]:
    if not os.path.exists(folder):
        os.makedirs(folder)