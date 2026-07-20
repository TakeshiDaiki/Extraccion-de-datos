import streamlit as st

from auth.service import get_plan, PLAN_LIMITS


def require_login():
    """Blocks access to a page if there's no active session.
    Must be called at the top of every protected page."""
    if "user_email" not in st.session_state:
        st.warning("🔒 You need to log in to view this page.")
        st.page_link("views/login.py", label="Go to Login", icon="🔑")
        st.stop()


def current_plan() -> dict:
    """Returns the logged-in user's plan configuration."""
    email = st.session_state.get("user_email")
    plan_name = get_plan(email) if email else "free"
    return {"name": plan_name, **PLAN_LIMITS[plan_name]}


def logout_button():
    if st.sidebar.button("🚪 Log out"):
        st.session_state.pop("user_email", None)
        st.rerun()
