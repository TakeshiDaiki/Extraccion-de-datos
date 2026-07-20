import streamlit as st

BRAND_NAME = "Master Data Explorer Pro"

# Warm editorial palette (cream + forest green), inspired by studio/agency
# sites rather than typical dark "tech SaaS" dashboards. Used app-wide via
# .streamlit/config.toml; the pill/blob/oversized-type treatment below is
# reserved for the public marketing pages (landing, login, register,
# forgot-password, plans) — the Dashboard stays plain so dense data tables
# remain readable.
CREAM = "#FBF3E7"
CARD = "#FFFFFF"
FOREST = "#1C3829"
FOREST_DARK = "#12271B"
INK = "#1A2A20"
MUTED = "#7C8B7E"
BLOB_BLUE = "#C9D8F3"
BLOB_LILAC = "#DCCFEF"

def inject_base_style():
    """Injects shared CSS. Cheap and idempotent, so it's re-emitted on every
    run rather than cached behind a session_state flag — Streamlit can drop
    a markdown element that isn't re-issued at the same script position on a
    later rerun (e.g. after st.rerun()), which silently strips the CSS."""
    st.markdown(f"""
    <style>
        .brand-header {{
            font-weight: 800;
            font-size: 2.1rem;
            border-left: 6px solid {FOREST};
            padding-left: 16px;
            margin-bottom: 0.3rem;
            line-height: 1.3;
            color: {INK};
        }}
        .brand-subtitle {{
            color: {MUTED};
            font-size: 1.05rem;
            padding-left: 22px;
            margin-bottom: 1.5rem;
            max-width: 780px;
        }}
        .section-title {{
            font-weight: 700;
            font-size: 1.4rem;
            margin-top: 1rem;
            margin-bottom: 0.8rem;
            color: {INK};
        }}
        .stTabs [data-baseweb="tab"] {{ font-weight: 600; }}
        div[data-testid="stForm"] {{
            border: 1px solid rgba(28,56,41,0.12);
            border-radius: 20px;
            padding: 1.6rem;
            background: {CARD};
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 20px;
        }}
        .feature-card {{
            border: 1px solid rgba(28,56,41,0.12);
            border-radius: 20px;
            padding: 1.2rem 1.4rem;
            height: 100%;
            background: {CARD};
        }}
        .feature-card h4 {{ margin-top: 0; color: {INK}; }}
        .muted {{ color: {MUTED}; }}

        /* Floating pill navigation (app-wide, including the Dashboard, so
           the chrome stays consistent even though the Dashboard skips the
           marketing styling below). */
        header[data-testid="stHeader"] {{
            background: {CREAM} !important;
        }}
        .rc-overflow {{
            background: {CARD} !important;
            border-radius: 999px !important;
            box-shadow: 0 6px 24px rgba(28,56,41,0.10);
        }}
        [data-testid="stTopNavLink"] {{
            border-radius: 999px !important;
            padding: 6px 16px !important;
            font-weight: 600 !important;
            color: {INK} !important;
        }}
        [data-testid="stTopNavLink"][aria-current="page"] {{
            background: {FOREST} !important;
            color: white !important;
        }}
    </style>
    """, unsafe_allow_html=True)


def inject_marketing_style():
    """Extra CSS for public-facing pages only: pill-shaped nav/buttons,
    organic blob backgrounds, oversized headline type. Call in addition to
    inject_base_style() (done automatically by render_header/render_hero).
    Re-emitted every run — see inject_base_style() for why it isn't cached."""
    st.markdown(f"""
    <style>
        /* Pill buttons everywhere on marketing pages. */
        .stButton > button,
        .stLinkButton > a,
        div[data-testid="stFormSubmitButton"] > button {{
            border-radius: 999px !important;
            font-weight: 700 !important;
        }}
        .stButton > button[kind="primary"],
        div[data-testid="stFormSubmitButton"] > button[kind="primary"] {{
            background-color: {FOREST} !important;
            border-color: {FOREST} !important;
        }}
        .stButton > button[kind="primary"]:hover {{
            background-color: {FOREST_DARK} !important;
            border-color: {FOREST_DARK} !important;
        }}

        /* Oversized editorial headline for hero sections. */
        .hero-title {{
            font-weight: 800;
            font-size: clamp(2.6rem, 6vw, 5rem);
            line-height: 1.02;
            letter-spacing: -0.02em;
            color: {FOREST};
            margin-bottom: 0.6rem;
        }}
        .hero-subtitle {{
            color: {MUTED};
            font-size: 1.15rem;
            max-width: 640px;
            margin-bottom: 1.6rem;
        }}
        .hero-wrap {{
            position: relative;
            padding: 1rem 0 2rem 0;
            overflow: hidden;
        }}
        .blob {{
            position: absolute;
            border-radius: 50%;
            filter: blur(2px);
            opacity: 0.55;
            z-index: -1;
        }}
        .blob-blue {{
            width: 340px; height: 340px;
            background: radial-gradient(circle at 30% 30%, {BLOB_BLUE}, transparent 70%);
            top: -60px; right: 8%;
        }}
        .blob-lilac {{
            width: 260px; height: 260px;
            background: radial-gradient(circle at 30% 30%, {BLOB_LILAC}, transparent 70%);
            top: 120px; right: 28%;
        }}

        /* Pill tag chips, used for feature/plan highlights. */
        .pill-tag {{
            display: inline-block;
            background: {CARD};
            border: 1px solid rgba(28,56,41,0.15);
            border-radius: 999px;
            padding: 6px 16px;
            margin: 0 8px 8px 0;
            font-size: 0.85rem;
            font-weight: 600;
            color: {INK};
        }}
    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = None, icon: str = "📑"):
    inject_base_style()
    st.markdown(f'<div class="brand-header">{icon} {title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="brand-subtitle">{subtitle}</div>', unsafe_allow_html=True)


def render_hero(title: str, subtitle: str = None):
    """Oversized editorial-style header with blob decorations, for the
    landing page and other marketing entry points."""
    inject_base_style()
    inject_marketing_style()
    st.markdown(
        f"""
        <div class="hero-wrap">
            <div class="blob blob-blue"></div>
            <div class="blob blob-lilac"></div>
            <div class="hero-title">{title}</div>
            {f'<div class="hero-subtitle">{subtitle}</div>' if subtitle else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
