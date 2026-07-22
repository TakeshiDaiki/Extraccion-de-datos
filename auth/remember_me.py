import streamlit as st
import streamlit.components.v1 as components

from auth.service import create_remember_token, revoke_remember_token, verify_remember_token

COOKIE_NAME = "ingestly_remember_token"
REMEMBER_DAYS = 30


def _set_cookie(token: str, days: int) -> None:
    # Streamlit has no first-party API to set cookies (st.context.cookies is
    # read-only). A <script> tag passed through st.markdown(unsafe_allow_html=True)
    # is inserted via innerHTML, which browsers deliberately never execute —
    # components.v1.html renders a real (sandboxed, but allow-same-origin)
    # iframe document instead, where <script> tags do run, and document.cookie
    # set there still applies to the app's real origin. st.context.cookies will
    # see it on the next request (new tab, reload, or later visit).
    max_age = days * 86400
    components.html(
        f'<script>document.cookie = "{COOKIE_NAME}={token}; max-age={max_age}; '
        f'path=/; SameSite=Lax";</script>',
        height=0,
    )


def _clear_cookie() -> None:
    components.html(
        f'<script>document.cookie = "{COOKIE_NAME}=; max-age=0; path=/; SameSite=Lax";</script>',
        height=0,
    )


def remember_login(email: str) -> None:
    """Call right after a successful login where the user checked "Remember me"."""
    token = create_remember_token(email, days=REMEMBER_DAYS)
    _set_cookie(token, REMEMBER_DAYS)


def forget_login() -> None:
    """Call on logout: revokes the stored token server-side and clears the cookie."""
    token = st.context.cookies.get(COOKIE_NAME)
    if token:
        revoke_remember_token(token)
    _clear_cookie()


def restore_session() -> None:
    """Auto-restores a logged-in session from the remember-me cookie, if any.
    Must run once per script, before any page checks st.session_state["user_email"]."""
    if "user_email" in st.session_state:
        return
    token = st.context.cookies.get(COOKIE_NAME)
    if not token:
        return
    email = verify_remember_token(token)
    if email:
        st.session_state["user_email"] = email
