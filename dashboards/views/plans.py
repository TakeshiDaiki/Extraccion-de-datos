import streamlit as st

from auth.guard import require_login, current_plan
from auth.service import set_plan, PLAN_LIMITS

require_login()
plan = current_plan()

st.markdown("## ⭐ Tu plan")
st.info(f"Plan actual: **{plan['label']}**")

st.markdown("---")
col_free, col_premium = st.columns(2)

with col_free:
    free = PLAN_LIMITS["free"]
    with st.container(border=True):
        st.markdown("#### Free — $0/mes")
        st.write(f"Hasta {free['max_records']} registros por extracción")
        st.write(f"Fuentes: {', '.join(s.upper() for s in free['sources'])}")
        if plan["name"] == "free":
            st.success("Plan actual")
        else:
            if st.button("Volver a Free", use_container_width=True):
                set_plan(st.session_state["user_email"], "free")
                st.rerun()

with col_premium:
    premium = PLAN_LIMITS["premium"]
    with st.container(border=True):
        st.markdown("#### ⭐ Premium — $19/mes")
        st.write(f"Hasta {premium['max_records']:,} registros por extracción")
        st.write("Las 6 fuentes + reglas de automatización + exportación a Excel")
        if plan["name"] == "premium":
            st.success("Plan actual")
        else:
            if st.button("⭐ Actualizar a Premium", use_container_width=True, type="primary"):
                set_plan(st.session_state["user_email"], "premium")
                st.rerun()

st.caption(
    "💡 Demo: este botón cambia tu plan al instante, no hay ningún cobro real ni "
    "procesador de pagos conectado."
)
