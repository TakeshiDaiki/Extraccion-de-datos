import streamlit as st

from auth.service import PLAN_LIMITS
from views._style import render_hero, BRAND_NAME

render_hero(
    BRAND_NAME,
    "A business intelligence platform built for data people — pull data from 6 different "
    "sources, clean and transform it with a professional toolkit, and explore it all from "
    "one interactive dashboard, backed by an AI-assisted extraction workflow.",
)

st.markdown(
    '<span class="pill-tag">🧩 6 extraction engines</span>'
    '<span class="pill-tag">🧹 Cleaning toolkit</span>'
    '<span class="pill-tag">🔁 Automation rules</span>'
    '<span class="pill-tag">📤 CSV & Excel export</span>',
    unsafe_allow_html=True,
)

if "user_email" in st.session_state:
    st.success(f"You're logged in as **{st.session_state['user_email']}**.")
    st.page_link("views/dashboard.py", label="Go to Dashboard", icon="📊")
else:
    c1, c2 = st.columns(2)
    with c1:
        st.page_link("views/register.py", label="Create a free account", icon="📝")
    with c2:
        st.page_link("views/login.py", label="Already have an account — Log in", icon="🔑")

st.markdown("---")

# --- WHAT IS IT ---
st.markdown('<div class="section-title">What is Ingestly?</div>', unsafe_allow_html=True)
st.write(
    "Most data work isn't the analysis itself — it's the hours lost wrangling spreadsheets, "
    "scraped pages, inboxes, and PDFs into something you can actually chart. Ingestly "
    "handles that grind for you: point it at a source, let the extraction engine "
    "pull the data, and use the built-in cleaning suite to get it analysis-ready in minutes, "
    "not hours."
)

st.markdown("<br>", unsafe_allow_html=True)

# --- HOW IT WORKS ---
st.markdown('<div class="section-title">How it works</div>', unsafe_allow_html=True)
h1, h2, h3 = st.columns(3)
with h1:
    st.markdown(
        '<div class="feature-card"><h4>1. Connect a source</h4>'
        '<p class="muted">Choose from 6 extraction engines — web, API, authenticated logins, '
        'email, PDF, or Excel — and pull data on demand or on a schedule.</p></div>',
        unsafe_allow_html=True,
    )
with h2:
    st.markdown(
        '<div class="feature-card"><h4>2. Clean & transform</h4>'
        '<p class="muted">Deduplicate, normalize text, build calculated columns, and save '
        'automation rules so the same cleanup runs itself on every future extraction.</p></div>',
        unsafe_allow_html=True,
    )
with h3:
    st.markdown(
        '<div class="feature-card"><h4>3. Explore & export</h4>'
        '<p class="muted">Browse results in an interactive data editor, check column health at '
        'a glance, and export to CSV or Excel whenever you need to share it.</p></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- FEATURES ---
st.markdown('<div class="section-title">What you get</div>', unsafe_allow_html=True)
f1, f2, f3 = st.columns(3)
with f1:
    st.markdown(
        '<div class="feature-card"><h4>🧩 6 extraction engines</h4>'
        '<p class="muted">Web Scraping, API Extraction, Login Scraping, Email Extraction, '
        'PDF Processing, and Excel Processing — all from one assistant.</p></div>',
        unsafe_allow_html=True,
    )
with f2:
    st.markdown(
        '<div class="feature-card"><h4>🧹 Pro cleaning toolkit</h4>'
        '<p class="muted">Deduplication, text normalization, bulk find & replace, and '
        'formula-based calculated columns for every dataset.</p></div>',
        unsafe_allow_html=True,
    )
with f3:
    st.markdown(
        '<div class="feature-card"><h4>🔁 Saved automation rules</h4>'
        '<p class="muted">Define a cleanup once and it auto-applies on every future run — '
        'no repeating manual work (Premium).</p></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)
f4, f5, f6 = st.columns(3)
with f4:
    st.markdown(
        '<div class="feature-card"><h4>🔌 REST API</h4>'
        '<p class="muted">A FastAPI endpoint (<code>POST /run-etl</code>) to trigger the full '
        'pipeline from your own tools or a scheduler.</p></div>',
        unsafe_allow_html=True,
    )
with f5:
    st.markdown(
        '<div class="feature-card"><h4>📤 CSV & Excel export</h4>'
        '<p class="muted">Get your processed data out in the format your team already '
        'works with, in one click.</p></div>',
        unsafe_allow_html=True,
    )
with f6:
    st.markdown(
        '<div class="feature-card"><h4>👥 Built for teams</h4>'
        '<p class="muted">Individual accounts, so each analyst keeps their own extractions '
        'and rules separate.</p></div>',
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# --- WHO IS THIS FOR ---
st.markdown('<div class="section-title">Who it\'s for</div>', unsafe_allow_html=True)
st.write(
    "Independent data analysts, small ops and growth teams, and agencies that need to turn "
    "messy, scattered sources into clean datasets without maintaining their own scraping "
    "and ETL infrastructure."
)

st.markdown("---")

# --- PRICING ---
st.markdown('<div class="section-title">Plans</div>', unsafe_allow_html=True)

col_free, col_premium = st.columns(2)

with col_free:
    free = PLAN_LIMITS["free"]
    with st.container(border=True):
        st.markdown("#### Free")
        st.markdown("### $0 /month")
        st.write(f"✅ Up to **{free['max_records']}** records per extraction")
        st.write(f"✅ Sources: {', '.join(s.upper() for s in free['sources'])}")
        st.write("❌ Automation rules")
        st.write("❌ Excel, PDF, Login Scraping")

with col_premium:
    premium = PLAN_LIMITS["premium"]
    with st.container(border=True):
        st.markdown("#### ⭐ Premium")
        st.markdown("### $19 /month")
        st.write(f"✅ Up to **{premium['max_records']:,}** records per extraction")
        st.write("✅ All 6 extraction engines")
        st.write("✅ Automation rules (self-running cleanup)")
        st.write("✅ Excel export")

st.caption(
    "💡 Premium billing runs through real PayPal Subscriptions (currently in sandbox mode "
    "for testing — no real charges yet). See the Plans page for details."
)
