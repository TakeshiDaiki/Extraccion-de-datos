import streamlit as st

from auth.service import register_user
from views._style import render_header, inject_marketing_style

render_header("Create Account", icon="📝")
inject_marketing_style()
st.caption("You'll start on the Free plan automatically — upgrade to Premium anytime.")

if "user_email" in st.session_state:
    st.info(f"You're already logged in as **{st.session_state['user_email']}**.")
    st.page_link("views/dashboard.py", label="Go to Dashboard", icon="📊")
    st.stop()

if "new_recovery_key" not in st.session_state:
    with st.form("register_form"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        password2 = st.text_input("Confirm password", type="password")

        if st.form_submit_button("Create Account", use_container_width=True, type="primary"):
            if password != password2:
                st.error("Passwords don't match.")
            else:
                ok, message, recovery_key = register_user(email, password)
                if ok:
                    st.session_state["new_recovery_key"] = recovery_key
                    st.rerun()
                else:
                    st.error(message)

    st.markdown("---")
    st.caption("Already have an account?")
    st.page_link("views/login.py", label="Log in", icon="🔑")
else:
    st.success("Account created successfully.")
    st.warning(
        "**Save this recovery key now — it's the only way to reset your "
        "password later, and we can't show it to you again.**"
    )
    st.code(st.session_state["new_recovery_key"], language=None)
    st.caption("Write it down or store it in a password manager, then continue.")

    if st.button("I've saved my recovery key — continue to Log In", use_container_width=True, type="primary"):
        del st.session_state["new_recovery_key"]
        st.switch_page("views/login.py")
