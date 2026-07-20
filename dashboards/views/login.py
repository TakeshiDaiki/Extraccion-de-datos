import streamlit as st

from auth.service import authenticate

st.markdown("## 🔑 Iniciar Sesión")

if "user_email" in st.session_state:
    st.info(f"Ya iniciaste sesión como **{st.session_state['user_email']}**.")
    st.page_link("views/dashboard.py", label="Ir al Dashboard", icon="📊")
    st.stop()

with st.form("login_form"):
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")

    if st.form_submit_button("Iniciar Sesión", use_container_width=True):
        ok, message = authenticate(email, password)
        if ok:
            st.session_state["user_email"] = email.strip().lower()
            st.success(message)
            st.page_link("views/dashboard.py", label="Ir al Dashboard →", icon="📊")
        else:
            st.error(message)

st.markdown("---")
st.caption("¿No tenés cuenta todavía?")
st.page_link("views/register.py", label="Registrarse gratis", icon="📝")
