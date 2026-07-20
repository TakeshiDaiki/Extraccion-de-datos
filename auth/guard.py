import streamlit as st

from auth.service import get_plan, PLAN_LIMITS


def require_login():
    """Bloquea el acceso a una página si no hay sesión iniciada.
    Debe llamarse al principio de cada página protegida."""
    if "user_email" not in st.session_state:
        st.warning("🔒 Tenés que iniciar sesión para ver esta página.")
        st.page_link("views/login.py", label="Ir a Iniciar Sesión", icon="🔑")
        st.stop()


def current_plan() -> dict:
    """Devuelve la configuración del plan del usuario logueado."""
    email = st.session_state.get("user_email")
    plan_name = get_plan(email) if email else "free"
    return {"name": plan_name, **PLAN_LIMITS[plan_name]}


def logout_button():
    if st.sidebar.button("🚪 Cerrar sesión"):
        st.session_state.pop("user_email", None)
        st.rerun()
