import streamlit as st

from auth.service import request_password_reset, reset_password
from notifications.sendgrid_service import is_configured as email_is_configured
from views._style import render_header

render_header("Forgot Password", icon="🔓")

if "user_email" in st.session_state:
    st.info(f"You're already logged in as **{st.session_state['user_email']}**.")
    st.page_link("views/dashboard.py", label="Go to Dashboard", icon="📊")
    st.stop()

if not email_is_configured():
    st.warning(
        "Password reset emails aren't configured yet on this deployment. "
        "Contact support or try again later."
    )
    st.page_link("views/login.py", label="Back to Log In", icon="🔑")
    st.stop()

st.caption("We'll email you a 6-digit code to reset your password.")

with st.form("request_code_form"):
    email = st.text_input("Email")
    if st.form_submit_button("Send Reset Code", use_container_width=True):
        ok, message = request_password_reset(email)
        if ok:
            st.session_state["reset_email"] = email.strip().lower()
            st.success(message)
        else:
            st.error(message)

if "reset_email" in st.session_state:
    st.markdown("---")
    st.markdown(f'<div class="section-title">Enter your code</div>', unsafe_allow_html=True)
    st.caption(f"Sent to **{st.session_state['reset_email']}**")

    with st.form("reset_password_form"):
        code = st.text_input("6-digit code")
        new_password = st.text_input("New password", type="password")
        new_password2 = st.text_input("Confirm new password", type="password")

        if st.form_submit_button("Reset Password", use_container_width=True):
            if new_password != new_password2:
                st.error("Passwords don't match.")
            else:
                ok, message = reset_password(st.session_state["reset_email"], code, new_password)
                if ok:
                    del st.session_state["reset_email"]
                    st.success(message)
                    st.page_link("views/login.py", label="Log In →", icon="🔑")
                else:
                    st.error(message)

st.markdown("---")
st.page_link("views/login.py", label="Back to Log In", icon="🔑")
