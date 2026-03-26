import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect

# Configuración de arquitectura
from config import SQLITE_URL
from transform.cleaner import DataCleaner
from transform.normalizer import DataNormalizer
from transform.deduplicator import Deduplicator
from core.script_logger import log_transformation
from assistant.command_router import route_command

# Configuración de página
st.set_page_config(page_title="Data Explorer Pro", layout="wide", page_icon="🤖")
engine = create_engine(SQLITE_URL)

# --- ESTILOS PERSONALIZADOS ---
st.markdown("""
<style>
    .main-header { color: #1a508b; border-left: 6px solid #ff4b4b; padding-left: 15px; font-weight: 800; margin-bottom: 20px; }
    .stTabs [data-baseweb="tab"] { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# --- SIDEBAR: ASISTENTE DE IA (Control de Extracción) ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2103/2103633.png", width=70)
    st.markdown("### 🤖 BI Data Assistant")

    with st.form("extraction_assistant"):
        option = st.selectbox(
            "¿Qué motor deseas ejecutar?",
            ["1. Web Scraping", "2. Login Scraping", "3. API Extraction",
             "4. Email Extraction", "5. PDF Processing", "6. Excel Processing",
             "7. 🚀 PIPELINE COMPLETO"]
        )
        limit = st.number_input("Límite de registros:", min_value=1, value=100)
        target_url = st.text_input("URL (Si aplica):", placeholder="https://ejemplo.com")

        if st.form_submit_button("🚀 Iniciar Extracción", use_container_width=True):
            with st.status("Procesando...", expanded=True) as status:
                try:
                    # Enruta el comando directamente al motor
                    route_command(option[0], limit, target_url)
                    status.update(label="✅ Éxito", state="complete")
                    st.toast("Datos actualizados.")
                except Exception as e:
                    status.update(label=f"❌ Error: {str(e)}", state="error")


def render_excel_pro_view(table_name: str, label: str):
    """Vista de tabla profesional con herramientas ETL Avanzadas"""
    inspector = inspect(engine)
    if table_name not in inspector.get_table_names():
        st.warning(f"La fuente '{label}' aún no tiene datos cargados.")
        return

    df = pd.read_sql(table_name, engine)

    # --- DIAGNÓSTICO ---
    with st.expander("🩺 Diagnóstico de Salud"):
        c1, c2 = st.columns([3, 1])
        with c1: st.dataframe(DataCleaner.get_column_health(df), use_container_width=True, hide_index=True)
        with c2: st.metric("Registros", len(df))

    # --- SUITE DE TRANSFORMACIÓN (Punto 4, 5, 6, 7) ---
    tab_clean, tab_pro, tab_norm = st.tabs(["✨ Limpieza Básica", "🧹 Refinamiento Pro", "➕ Fórmulas"])

    with tab_clean:
        c1, c2, c3 = st.columns([2, 1, 1])
        with c1:
            target_col = st.selectbox("Deduplicar por:", ["-- Fila Completa --"] + df.columns.tolist(),
                                      key=f"d_{table_name}")
        with c2:
            st.write("")
            if st.button("🗑️ Deduplicar", use_container_width=True, key=f"bd_{table_name}"):
                df = Deduplicator.remove_duplicates(df, None if target_col == "-- Fila Completa --" else target_col)
                log_transformation(table_name, "DEDUPLICATE", f"Col: {target_col}")
                st.rerun()
        with c3:
            st.write("")
            if st.button("✂️ Trim & Headers", use_container_width=True, key=f"bt_{table_name}"):
                df = DataCleaner.trim_spaces(df)
                df = DataCleaner.normalize_headers(df)
                log_transformation(table_name, "CLEAN_BASE", "Trim and Header normalization")
                st.rerun()

    with tab_pro:
        # Punto 4: Funciones de Limpieza Avanzada
        st.markdown("##### 🧪 Transformación Semántica")
        cp1, cp2, cp3 = st.columns([2, 1, 1])
        with cp1:
            text_col = st.selectbox("Columna objetivo:", df.columns, key=f"tc_{table_name}")
        with cp2:
            mode = st.selectbox("Operación:", ["UPPER", "LOWER", "TITLE", "STRIP_ACCENTS"], key=f"tm_{table_name}")
        with cp3:
            st.write("")
            if st.button("Ejecutar Cambio", use_container_width=True, key=f"tb_{table_name}"):
                df = DataCleaner.advanced_text_process(df, text_col, mode)
                log_transformation(table_name, "TEXT_FORMAT", f"Col: {text_col}, Mode: {mode}")
                st.rerun()

        st.markdown("---")
        st.markdown("##### 🔄 Reemplazo Masivo")
        cr1, cr2, cr3 = st.columns(3)
        to_rep = cr1.text_input("Valor a buscar", key=f"tr_{table_name}")
        with_val = cr2.text_input("Reemplazar con", key=f"wv_{table_name}")
        if cr3.button("Aplicar Reemplazo", use_container_width=True, key=f"rb_{table_name}"):
            df = DataCleaner.mass_replace(df, text_col, to_rep, with_val)
            log_transformation(table_name, "MASS_REPLACE", f"In: {text_col}, {to_rep} -> {with_val}")
            st.rerun()

    with tab_norm:
        with st.form(f"f_calc_{table_name}"):
            c_name = st.text_input("Nombre de nueva columna")
            c_form = st.text_input("Fórmula (ej: precio * 0.15)")
            if st.form_submit_button("Añadir Columna"):
                df = DataNormalizer.add_calculated_column(df, c_name, c_form)
                log_transformation(table_name, "CALC_COL", f"{c_name}: {c_form}")
                st.rerun()

    # --- EDITOR Y EXPORTACIÓN ---
    st.markdown("---")
    st.data_editor(df, use_container_width=True, height=400, num_rows="dynamic", key=f"ed_{table_name}")
    st.download_button("📥 Exportar CSV Procesado", df.to_csv(index=False).encode('utf-8'), f"{table_name}_ready.csv")


# --- LAYOUT PRINCIPAL ---
st.markdown('<h1 class="main-header">📑 Master Data Explorer Pro</h1>', unsafe_allow_html=True)
t_web, t_api, t_mail, t_doc, t_auth = st.tabs(["🌐 Web", "🔗 API", "📧 Email", "📄 Docs", "🔐 Auth"])

with t_web: render_excel_pro_view("raw_web_data", "Web Scraper")
with t_api: render_excel_pro_view("raw_api_data", "API Records")
with t_mail: render_excel_pro_view("email_extraction_logs", "Emails")
with t_doc: render_excel_pro_view("raw_pdf_data", "Documentos")
with t_auth: render_excel_pro_view("raw_login_data", "Sesiones")