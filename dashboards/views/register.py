import streamlit as st

from auth.service import register_user

st.markdown("## 📝 Crear cuenta")
st.caption("Empezás automáticamente en el plan Free — podés pasarte a Premium cuando quieras.")

if "user_email" in st.session_state:
    st.info(f"Ya iniciaste sesión como **{st.session_state['user_email']}**.")
    st.page_link("views/dashboard.py", label="Ir al Dashboard", icon="📊")
    st.stop()

with st.form("register_form"):
    email = st.text_input("Email")
    password = st.text_input("Contraseña", type="password")
    password2 = st.text_input("Repetir contraseña", type="password")

    if st.form_submit_button("Crear cuenta", use_container_width=True):
        if password != password2:
            st.error("Las contraseñas no coinciden.")
        else:
            ok, message = register_user(email, password)
            if ok:
                st.success(message)
                st.page_link("views/login.py", label="Iniciar Sesión →", icon="🔑")
            else:
                st.error(message)

st.markdown("---")
st.caption("¿Ya tenés cuenta?")
st.page_link("views/login.py", label="Iniciar sesión", icon="🔑")
