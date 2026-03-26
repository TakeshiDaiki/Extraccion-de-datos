import subprocess
import sys
import os
from core.pipeline import run_pipeline


def setup_environment():
    """Asegura que las carpetas necesarias existan antes de empezar."""
    folders = ["scripts_used", "config", "data"]
    for folder in folders:
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"📁 Carpeta verificada/creada: {folder}")


def run_all():
    """
    Launcher principal del sistema BI Intelligence.
    Ejecuta la extracción masiva y levanta la interfaz visual de Streamlit.
    """
    print("=" * 50)
    print("🚀 MASTER ETL CONTROL - BI PLATFORM")
    print("=" * 50)

    # 0. Preparación de entorno
    setup_environment()

    # 1. EJECUCIÓN DEL PIPELINE MAESTRO (Extracción Inicial)
    print("\n[STEP 1/2] Iniciando motores de extracción masiva...")

    current_filters = {
        "categories": ["Tech", "Books"],
        "min_value": 10,
        "keywords": ["AI", "Data", "Cloud"]
    }

    try:
        # Ejecutamos una extracción de prueba para poblar la base de datos
        pipeline_results = run_pipeline(
            sources=["web", "api", "email", "excel", "pdf", "login"],
            limit=50,
            filters=current_filters
        )

        success_count = len(pipeline_results.get("success", []))
        print(f"✅ Extracción finalizada. Motores exitosos: {success_count}/6")

    except Exception as e:
        print(f"⚠️ Nota: No se pudo completar la extracción inicial ({e}).")
        print("Abriendo el Dashboard con los datos disponibles actualmente...")

    # 2. LANZAMIENTO DEL DASHBOARD (Interfaz de Usuario)
    print("\n[STEP 2/2] Levantando Dashboard BI en Streamlit...")

    app_path = os.path.join("dashboards", "streamlit_app.py")

    process = None
    try:
        # Lanzamos el proceso de Streamlit
        process = subprocess.Popen([
            sys.executable,
            "-m",
            "streamlit",
            "run",
            app_path
        ])

        print("\n" + "*" * 40)
        print("✨ SISTEMA OPERATIVO Y DISPONIBLE")
        print("🌍 Revisa tu navegador en http://localhost:8501")
        print("💡 Presiona CTRL+C para cerrar el servidor.")
        print("*" * 40 + "\n")

        # Esperamos a que el proceso termine (o sea interrumpido)
        process.wait()

    except KeyboardInterrupt:
        print("\n🛑 Deteniendo Master Control...")
        if process:
            process.terminate()
            process.wait()
        print("👋 ¡Cierre de sistema exitoso!")

    except Exception as e:
        print(f"\n❌ Error crítico al lanzar el Dashboard: {e}")
        if process:
            process.kill()


if __name__ == "__main__":
    run_all()