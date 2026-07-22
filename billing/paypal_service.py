import os
import urllib.parse

import requests
import streamlit as st

SANDBOX_BASE_URL = "https://api-m.sandbox.paypal.com"
LIVE_BASE_URL = "https://api-m.paypal.com"


def _secret(key: str, default: str = "") -> str:
    """Reads a PayPal config value from Streamlit secrets first (used both
    locally via .streamlit/secrets.toml and on Streamlit Community Cloud via
    its Secrets settings), falling back to an env var of the same name."""
    try:
        value = st.secrets.get("paypal", {}).get(key, "")
    except Exception:
        value = ""
    if value:
        return value
    return os.environ.get(f"PAYPAL_{key.upper()}", default)


def is_configured() -> bool:
    return bool(_secret("client_id")) and bool(_secret("client_secret")) and bool(_secret("plan_id"))


def is_live() -> bool:
    return _secret("mode", "sandbox") == "live"


def _base_url() -> str:
    return LIVE_BASE_URL if _secret("mode", "sandbox") == "live" else SANDBOX_BASE_URL


def _app_base_url() -> str:
    return _secret("app_base_url", "http://localhost:8501").rstrip("/")


def _access_token() -> str:
    """PayPal's REST API is authenticated with a short-lived OAuth2 bearer
    token (client_credentials grant) rather than a static secret key, so we
    fetch a fresh one per call — checkout/verification calls here are rare
    enough that the extra round trip doesn't matter."""
    response = requests.post(
        f"{_base_url()}/v1/oauth2/token",
        auth=(_secret("client_id"), _secret("client_secret")),
        data={"grant_type": "client_credentials"},
        timeout=15,
    )
    response.raise_for_status()
    return response.json()["access_token"]


def _headers() -> dict:
    return {
        "Authorization": f"Bearer {_access_token()}",
        "Content-Type": "application/json",
    }


def create_subscription(user_email: str) -> tuple[str, str]:
    """Creates a PayPal subscription in the pending-approval state. Returns
    (subscription_id, approve_url) — send the user to approve_url, and keep
    subscription_id to verify status when they come back."""
    base_url = _app_base_url()
    email_param = urllib.parse.quote(user_email)

    response = requests.post(
        f"{_base_url()}/v1/billing/subscriptions",
        headers=_headers(),
        json={
            "plan_id": _secret("plan_id"),
            "subscriber": {"email_address": user_email},
            "application_context": {
                "brand_name": "Ingestly",
                # paypal_return=1 is our own marker, not something PayPal adds — we
                # can't rely on PayPal appending a recognizable param on approval,
                # so we control the trigger for "user came back" ourselves. The
                # round trip through PayPal's domain always kills Streamlit's
                # in-memory session (even same-tab), so we can't rely on
                # st.session_state surviving — we carry the subscriber's email
                # here instead, since we set this URL ourselves and PayPal can't
                # alter it.
                "return_url": f"{base_url}/plans?paypal_return=1&email={email_param}",
                "cancel_url": f"{base_url}/plans?checkout=canceled",
                "user_action": "SUBSCRIBE_NOW",
            },
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    approve_url = next(link["href"] for link in data["links"] if link["rel"] == "approve")
    return data["id"], approve_url


def verify_subscription(subscription_id: str, user_email: str) -> tuple[bool, str]:
    """Confirms a subscription was actually approved and activated before
    granting Premium (instead of trusting the redirect alone, which a user
    could hit manually without approving)."""
    try:
        response = requests.get(
            f"{_base_url()}/v1/billing/subscriptions/{subscription_id}",
            headers=_headers(),
            timeout=15,
        )
        response.raise_for_status()
    except requests.exceptions.RequestException as exc:
        return False, f"Couldn't reach PayPal to verify this subscription ({exc})."
    data = response.json()

    if data.get("status") != "ACTIVE":
        return False, f"Subscription isn't active yet (status: {data.get('status')})."

    approved_email = data.get("subscriber", {}).get("email_address") or ""
    if approved_email.strip().lower() != user_email.strip().lower():
        return False, "This subscription doesn't belong to your account."

    return True, "Payment confirmed."


def cancel_subscription(subscription_id: str) -> None:
    """Cancels a real PayPal subscription immediately. Used when a user
    downgrades to Free, so they actually stop being billed instead of just
    flipping a local flag."""
    response = requests.post(
        f"{_base_url()}/v1/billing/subscriptions/{subscription_id}/cancel",
        headers=_headers(),
        json={"reason": "User downgraded to Free plan"},
        timeout=15,
    )
    response.raise_for_status()
