import os
from datetime import datetime
from functools import wraps

# Configuración de rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_FILE = os.path.join(BASE_DIR, "scripts_used", "audit_details.txt")


def audit_execution(script_name: str):
    """
    DECORADOR: Audita motores de extracción (Scrapers, API, etc.)
    Registra START, SUCCESS o ERROR automáticamente.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = datetime.now()
            log_event(script_name, "START", "Automatic extraction started")
            try:
                result = func(*args, **kwargs)
                duration = (datetime.now() - start_time).total_seconds()
                log_event(
                    script_name,
                    "SUCCESS",
                    f"Completed in {duration:.2f}s | Output: {result}"
                )
                return result
            except Exception as e:
                log_event(script_name, "ERROR", f"Failed: {str(e)}")
                raise

        return wrapper

    return decorator


def log_transformation(table_name: str, action: str, details: str):
    """
    MANUAL: Registra acciones del usuario en el Dashboard (Excel Pro).
    Cumple con el Punto 9 del historial de transformaciones.
    """
    log_event(f"UI:{table_name}", action, details)


def log_event(source, status, details):
    """Motor interno de escritura de logs"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {source.upper()} | {status} | {details}\n"

    # Asegurar que la carpeta scripts_used existe
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(entry)
    except IOError:
        pass