import os

import requests
import streamlit as st

SENDGRID_API_URL = "https://api.sendgrid.com/v3/mail/send"


def _secret(key: str, default: str = "") -> str:
    """Reads a SendGrid config value from Streamlit secrets first (local
    .streamlit/secrets.toml, or Streamlit Cloud's Secrets settings in prod),
    falling back to an env var of the same name — mirrors billing/paypal_service.py."""
    try:
        value = st.secrets.get("sendgrid", {}).get(key, "")
    except Exception:
        value = ""
    if value:
        return value
    return os.environ.get(f"SENDGRID_{key.upper()}", default)


def is_configured() -> bool:
    return bool(_secret("api_key")) and bool(_secret("from_email"))


def send_reset_code(to_email: str, code: str) -> tuple[bool, str]:
    """Sends a password-reset code via SendGrid's Mail Send API. Returns
    (ok, message) — callers should show `message` on failure without leaking
    API internals to the user."""
    if not is_configured():
        return False, "Email delivery isn't configured yet."

    payload = {
        "personalizations": [{"to": [{"email": to_email}]}],
        "from": {"email": _secret("from_email"), "name": "Master Data Explorer Pro"},
        "subject": "Your password reset code",
        "content": [{
            "type": "text/plain",
            "value": (
                f"Your password reset code is: {code}\n\n"
                "This code expires in 15 minutes. If you didn't request a "
                "password reset, you can safely ignore this email."
            ),
        }],
    }

    try:
        response = requests.post(
            SENDGRID_API_URL,
            headers={
                "Authorization": f"Bearer {_secret('api_key')}",
                "Content-Type": "application/json",
            },
            json=payload,
            timeout=15,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        return False, f"Couldn't send the reset email ({exc})."

    return True, "Reset code sent."
