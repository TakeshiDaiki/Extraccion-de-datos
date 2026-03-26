import streamlit as st


def render_ai_assistant():
    """Versión visual del asistente para la interfaz Streamlit"""
    st.sidebar.markdown("### 🤖 BI Intelligence Assistant")

    with st.sidebar.expander("🚀 Lanzar Motores de Extracción", expanded=True):
        option = st.selectbox(
            "¿Qué datos deseas extraer?",
            [
                "1. Web Scraping",
                "2. Login Scraping",
                "3. API Extraction",
                "4. Email Extraction",
                "5. PDF Processing",
                "6. Excel Processing",
                "7. 🚀 EJECUTAR PIPELINE COMPLETO"
            ]
        )

        limit = st.number_input("Límite de registros:", min_value=1, max_value=10000, value=100)

        # Campos condicionales según la opción
        url = ""
        if "Web" in option or "Login" in option:
            url = st.text_input("🌐 Ingrese URL objetivo:")

        if st.button("Ejecutar Comando", use_container_width=True):
            return option[0], limit, url  # Retornamos el número de opción, límite y URL

    return None, None, None