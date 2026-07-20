import streamlit as st

st.set_page_config(page_title="Data Explorer Pro", layout="wide", page_icon="🤖")

pages = [
    st.Page("views/landing.py", title="Inicio", icon="🏠", default=True),
    st.Page("views/login.py", title="Iniciar Sesión", icon="🔑"),
    st.Page("views/register.py", title="Registrarse", icon="📝"),
    st.Page("views/dashboard.py", title="Dashboard", icon="📊"),
    st.Page("views/plans.py", title="Planes", icon="⭐"),
]

st.navigation(pages).run()
