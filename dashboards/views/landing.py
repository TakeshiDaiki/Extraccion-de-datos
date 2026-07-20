import streamlit as st

from auth.service import PLAN_LIMITS

st.markdown(
    '<h1 style="color:#1a508b;border-left:6px solid #ff4b4b;padding-left:15px;'
    'font-weight:800;">📑 Master Data Explorer Pro</h1>',
    unsafe_allow_html=True,
)
st.markdown(
    "##### La plataforma BI para gente que se dedica al análisis de datos: "
    "extraé, limpiá y explorá tus datos desde 6 fuentes distintas, con un asistente de IA."
)

st.markdown("---")

if "user_email" in st.session_state:
    st.success(f"Sesión iniciada como **{st.session_state['user_email']}**.")
    st.page_link("views/dashboard.py", label="Ir al Dashboard", icon="📊")
else:
    c1, c2 = st.columns(2)
    with c1:
        st.page_link("views/register.py", label="Crear cuenta gratis", icon="📝")
    with c2:
        st.page_link("views/login.py", label="Ya tengo cuenta — Iniciar sesión", icon="🔑")

st.markdown("---")
st.markdown("### Planes")

col_free, col_premium = st.columns(2)

with col_free:
    free = PLAN_LIMITS["free"]
    with st.container(border=True):
        st.markdown("#### Free")
        st.markdown("### $0 /mes")
        st.write(f"✅ Hasta **{free['max_records']}** registros por extracción")
        st.write(f"✅ Fuentes: {', '.join(s.upper() for s in free['sources'])}")
        st.write("❌ Reglas de automatización")
        st.write("❌ Excel, PDF, Login Scraping")

with col_premium:
    premium = PLAN_LIMITS["premium"]
    with st.container(border=True):
        st.markdown("#### ⭐ Premium")
        st.markdown("### $19 /mes")
        st.write(f"✅ Hasta **{premium['max_records']:,}** registros por extracción")
        st.write("✅ Las 6 fuentes de extracción")
        st.write("✅ Reglas de automatización (limpieza automática)")
        st.write("✅ Exportación a Excel")

st.caption(
    "💡 Esta es una demo: los planes son una maqueta funcional, todavía no hay "
    "ningún procesador de pagos conectado — no se cobra dinero real."
)
