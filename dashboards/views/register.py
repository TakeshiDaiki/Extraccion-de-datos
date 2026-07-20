import streamlit as st

from auth.service import register_user
from views._style import render_header

render_header("Create Account", icon="📝")
st.caption("You'll start on the Free plan automatically — upgrade to Premium anytime.")

if "user_email" in st.session_state:
    st.info(f"You're already logged in as **{st.session_state['user_email']}**.")
    st.page_link("views/dashboard.py", label="Go to Dashboard", icon="📊")
    st.stop()

with st.form("register_form"):
    email = st.text_input("Email")
    password = st.text_input("Password", type="password")
    password2 = st.text_input("Confirm password", type="password")

    if st.form_submit_button("Create Account", use_container_width=True):
        if password != password2:
            st.error("Passwords don't match.")
        else:
            ok, message = register_user(email, password)
            if ok:
                st.success(message)
                st.page_link("views/login.py", label="Log In →", icon="🔑")
            else:
                st.error(message)

st.markdown("---")
st.caption("Already have an account?")
st.page_link("views/login.py", label="Log in", icon="🔑")
