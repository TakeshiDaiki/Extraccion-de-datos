import streamlit as st

BRAND_NAME = "Master Data Explorer Pro"
PRIMARY = "#6C5CE7"
MUTED = "#9CA3AF"

_INJECTED_KEY = "_base_style_injected"


def inject_base_style():
    """Injects shared CSS once per session. Safe to call from every page."""
    if st.session_state.get(_INJECTED_KEY):
        return
    st.session_state[_INJECTED_KEY] = True

    st.markdown(f"""
    <style>
        .brand-header {{
            font-weight: 800;
            font-size: 2.1rem;
            border-left: 6px solid {PRIMARY};
            padding-left: 16px;
            margin-bottom: 0.3rem;
            line-height: 1.3;
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
        }}
        .stTabs [data-baseweb="tab"] {{ font-weight: 600; }}
        div[data-testid="stForm"] {{
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 1.6rem;
        }}
        div[data-testid="stVerticalBlockBorderWrapper"] {{
            border-radius: 14px;
        }}
        .feature-card {{
            border: 1px solid rgba(255,255,255,0.08);
            border-radius: 14px;
            padding: 1.2rem 1.4rem;
            height: 100%;
        }}
        .feature-card h4 {{ margin-top: 0; }}
        .muted {{ color: {MUTED}; }}
    </style>
    """, unsafe_allow_html=True)


def render_header(title: str, subtitle: str = None, icon: str = "📑"):
    inject_base_style()
    st.markdown(f'<div class="brand-header">{icon} {title}</div>', unsafe_allow_html=True)
    if subtitle:
        st.markdown(f'<div class="brand-subtitle">{subtitle}</div>', unsafe_allow_html=True)
