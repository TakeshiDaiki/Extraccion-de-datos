import streamlit as st

from auth.service import reset_password_with_recovery_key
from views._style import render_header, inject_marketing_style

render_header("Reset Password", icon="🔓")
inject_marketing_style()

if "user_email" in st.session_state:
    st.info(f"You're already logged in as **{st.session_state['user_email']}**.")
    st.page_link("views/dashboard.py", label="Go to Dashboard", icon="📊")
    st.stop()

st.caption("Enter the recovery key you saved when you created your account.")

with st.form("reset_password_form"):
    email = st.text_input("Email")
    recovery_key = st.text_input("Recovery key", placeholder="XXXX-XXXX-XXXX-XXXX")
    new_password = st.text_input("New password", type="password")
    new_password2 = st.text_input("Confirm new password", type="password")

    if st.form_submit_button("Reset Password", use_container_width=True, type="primary"):
        if new_password != new_password2:
            st.error("Passwords don't match.")
        else:
            ok, message = reset_password_with_recovery_key(email, recovery_key, new_password)
            if ok:
                st.success(message)
                st.page_link("views/login.py", label="Log In →", icon="🔑")
            else:
                st.error(message)

st.markdown("---")
st.page_link("views/login.py", label="Back to Log In", icon="🔑")
