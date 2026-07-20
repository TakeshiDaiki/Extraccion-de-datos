import os
import sys

import streamlit as st

# Asegura que la raíz del repo esté en sys.path para los imports absolutos
# (auth.*, core.*, config, etc.), sin depender de cómo se lance el proceso
# (localmente vs. en Streamlit Community Cloud, que usa otro cwd).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

st.set_page_config(page_title="Master Data Explorer Pro", layout="wide", page_icon="🤖")

pages = [
    st.Page("views/landing.py", title="Home", icon="🏠", default=True),
    st.Page("views/login.py", title="Log In", icon="🔑"),
    st.Page("views/register.py", title="Sign Up", icon="📝"),
    st.Page("views/dashboard.py", title="Dashboard", icon="📊"),
    st.Page("views/plans.py", title="Plans", icon="⭐", url_path="plans"),
]

st.navigation(pages).run()
