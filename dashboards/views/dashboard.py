import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, inspect

from config import SQLITE_URL
from transform.cleaner import DataCleaner
from transform.normalizer import DataNormalizer
from transform.deduplicator import Deduplicator
from core.script_logger import log_transformation
from core.pipeline_manager import PipelineManager
from core.pipeline import run_pipeline
from assistant.command_router import route_command
from load.exporter import Exporter
from auth.guard import require_login, current_plan, logout_button

require_login()
plan = current_plan()
engine = create_engine(SQLITE_URL)

# Fuente -> (tabla, etiqueta, opción del asistente)
SOURCE_INFO = {
    "web": ("raw_web_data", "Web Scraper", "1. Web Scraping"),
    "login": ("raw_login_data", "Sesiones", "2. Login Scraping"),
    "api": ("raw_api_data", "API Records", "3. API Extraction"),
    "email": ("email_extraction_logs", "Emails", "4. Email Extraction"),
    "pdf": ("raw_pdf_data", "Documentos", "5. PDF Processing"),
    "excel": ("raw_excel_data", "Excel", "6. Excel Processing"),
}

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
    st.caption(f"Plan: **{plan['label']}**" + ("" if plan["name"] == "premium" else " · [Mejorar a Premium](/plans)"))

    allowed_labels = [SOURCE_INFO[s][2] for s in SOURCE_INFO if s in plan["sources"]]
    engine_options = allowed_labels + ["7. 🚀 PIPELINE COMPLETO"]

    with st.form("extraction_assistant"):
        option = st.selectbox("¿Qué motor deseas ejecutar?", engine_options)
        limit = st.number_input(
            "Límite de registros:", min_value=1, max_value=plan["max_records"], value=min(100, plan["max_records"])
        )
        target_url = st.text_input("URL (Si aplica):", placeholder="https://ejemplo.com")

        if st.form_submit_button("🚀 Iniciar Extracción", use_container_width=True):
            with st.status("Procesando...", expanded=True) as status:
                try:
                    if option[0] == "7":
                        # Pipeline completo: respeta las fuentes habilitadas por el plan
                        run_pipeline(sources=plan["sources"], limit=limit)
                    else:
                        route_command(option[0], limit, target_url)
                    status.update(label="✅ Éxito", state="complete")
                    st.toast("Datos actualizados.")
                except Exception as e:
                    status.update(label=f"❌ Error: {str(e)}", state="error")

    if plan["name"] != "premium":
        locked = [SOURCE_INFO[s][1] for s in SOURCE_INFO if s not in plan["sources"]]
        st.caption(f"🔒 Con Premium también accedés a: {', '.join(locked)}")

    logout_button()


def render_excel_pro_view(table_name: str, label: str, automation_enabled: bool):
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
    tab_labels = ["✨ Limpieza Básica", "🧹 Refinamiento Pro", "➕ Fórmulas"]
    if automation_enabled:
        tab_labels.append("⚙️ Automatización")
    tabs = st.tabs(tab_labels)
    tab_clean, tab_pro, tab_norm = tabs[0], tabs[1], tabs[2]
    tab_auto = tabs[3] if automation_enabled else None

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

    if automation_enabled:
        with tab_auto:
            # Punto 11: Reglas que se aplican automáticamente en cada corrida del
            # pipeline (core.pipeline_manager.PipelineManager.apply_stored_rules),
            # sin que el usuario tenga que repetir la limpieza manualmente cada vez.
            st.markdown("##### 🔁 Reglas que se aplican automáticamente en cada extracción")

            existing_rules = PipelineManager.get_rules(table_name)
            if existing_rules:
                for i, rule in enumerate(existing_rules):
                    rc1, rc2 = st.columns([5, 1])
                    with rc1:
                        st.write(f"**{rule['action']}** — {rule.get('params', {})}")
                    with rc2:
                        if st.button("🗑️", key=f"del_rule_{table_name}_{i}"):
                            PipelineManager.delete_rule(table_name, i)
                            st.rerun()
            else:
                st.caption("Todavía no hay reglas guardadas para esta fuente.")

            st.markdown("---")
            st.markdown("##### ➕ Guardar nueva regla")
            new_action = st.selectbox(
                "Acción:", ["DEDUPLICATE", "CLEAN_TEXT", "NEW_COLUMN"], key=f"rule_action_{table_name}"
            )

            new_params = {}
            if new_action == "DEDUPLICATE":
                rule_col = st.selectbox(
                    "Deduplicar por:", ["-- Fila Completa --"] + df.columns.tolist(), key=f"rule_col_{table_name}"
                )
                new_params = {"column": None if rule_col == "-- Fila Completa --" else rule_col}
            elif new_action == "NEW_COLUMN":
                rc1, rc2 = st.columns(2)
                rule_name = rc1.text_input("Nombre de columna", key=f"rule_name_{table_name}")
                rule_formula = rc2.text_input("Fórmula", key=f"rule_formula_{table_name}")
                new_params = {"name": rule_name, "formula": rule_formula}

            if st.button("💾 Guardar Regla", use_container_width=True, key=f"save_rule_{table_name}"):
                PipelineManager.save_rule(table_name, new_action, new_params)
                log_transformation(table_name, "RULE_SAVED", f"{new_action}: {new_params}")
                st.rerun()

    # --- EDITOR Y EXPORTACIÓN ---
    st.markdown("---")
    st.data_editor(df, use_container_width=True, height=400, num_rows="dynamic", key=f"ed_{table_name}")

    c_exp1, c_exp2 = st.columns(2)
    with c_exp1:
        st.download_button("📥 Exportar CSV Procesado", df.to_csv(index=False).encode('utf-8'), f"{table_name}_ready.csv")
    with c_exp2:
        if st.button("📊 Generar Excel", use_container_width=True, key=f"xlsx_btn_{table_name}"):
            path = Exporter().to_excel(df, f"{table_name}_ready")
            with open(path, "rb") as f:
                st.session_state[f"xlsx_bytes_{table_name}"] = f.read()
        if f"xlsx_bytes_{table_name}" in st.session_state:
            st.download_button(
                "⬇️ Descargar Excel",
                st.session_state[f"xlsx_bytes_{table_name}"],
                f"{table_name}_ready.xlsx",
                key=f"xlsx_dl_{table_name}"
            )


# --- LAYOUT PRINCIPAL ---
st.markdown('<h1 class="main-header">📑 Master Data Explorer Pro</h1>', unsafe_allow_html=True)

allowed_sources = [s for s in SOURCE_INFO if s in plan["sources"]]
tab_icons = {"web": "🌐", "api": "🔗", "email": "📧", "pdf": "📄", "login": "🔐", "excel": "📊"}
main_tabs = st.tabs([f"{tab_icons[s]} {SOURCE_INFO[s][1]}" for s in allowed_sources])

for tab, source in zip(main_tabs, allowed_sources):
    table_name, label, _ = SOURCE_INFO[source]
    with tab:
        render_excel_pro_view(table_name, label, automation_enabled=plan["automation_rules"])

if plan["name"] != "premium":
    st.markdown("---")
    locked = [SOURCE_INFO[s][1] for s in SOURCE_INFO if s not in plan["sources"]]
    st.info(f"🔒 Con el plan Premium también verías acá: **{', '.join(locked)}**")
    st.page_link("views/plans.py", label="Ver planes", icon="⭐")
