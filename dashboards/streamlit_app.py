import os
import sys

import streamlit as st

# Asegura que la raíz del repo esté en sys.path para los imports absolutos
# (auth.*, core.*, config, etc.), sin depender de cómo se lance el proceso
# (localmente vs. en Streamlit Community Cloud, que usa otro cwd).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if REPO_ROOT not in sys.path:
    sys.path.insert(0, REPO_ROOT)

from auth.remember_me import restore_session

st.set_page_config(page_title="Ingestly", layout="wide", page_icon="🤖")
restore_session()

pages = [
    st.Page("views/landing.py", title="Home", default=True),
    st.Page("views/login.py", title="Log In"),
    st.Page("views/register.py", title="Sign Up"),
    # Reachable at /forgot-password and linked from the Log In page, but
    # intentionally hidden from the top nav (see _style.py) — it's not a
    # primary destination like the others.
    st.Page("views/forgot_password.py", title="Forgot Password", url_path="forgot-password"),
    st.Page("views/dashboard.py", title="Dashboard"),
    st.Page("views/plans.py", title="Plans", url_path="plans"),
]

st.navigation(pages, position="top").run()
