import streamlit as st

from auth.service import authenticate
from auth.remember_me import remember_login
from views._style import render_header, inject_marketing_style

render_header("Log In", icon="🔑")
inject_marketing_style()

if "user_email" in st.session_state:
    st.info(f"You're already logged in as **{st.session_state['user_email']}**.")
    st.page_link("views/dashboard.py", label="Go to Dashboard", icon="📊")
    st.stop()

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    remember = st.checkbox("Remember me for 30 days")

    st.page_link("views/forgot_password.py", label="Forgot your password?", icon="🔓")

    if st.form_submit_button("Log In", use_container_width=True, type="primary"):
        ok, message = authenticate(email, password)
        if ok:
            st.session_state["user_email"] = email.strip().lower()
            if remember:
                remember_login(st.session_state["user_email"])
            st.success(message)
            st.page_link("views/dashboard.py", label="Go to Dashboard →", icon="📊")
        else:
            st.error(message)

st.markdown("---")
st.caption("Don't have an account yet?")
st.page_link("views/register.py", label="Sign up for free", icon="📝")
