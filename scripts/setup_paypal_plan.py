"""One-off helper: creates the "Premium" product and its $19/month recurring
billing plan in your PayPal account (sandbox by default), then prints the
plan ID and writes it into .streamlit/secrets.toml automatically.

Usage (from the repo root, with your virtualenv active) — reads client_id,
client_secret and mode straight from .streamlit/secrets.toml's [paypal]
table, the same file the app itself uses:
    python scripts/setup_paypal_plan.py

Or override via env vars if you'd rather not touch secrets.toml:
    PAYPAL_CLIENT_ID=... PAYPAL_CLIENT_SECRET=... PAYPAL_MODE=live python scripts/setup_paypal_plan.py

Run this once per PayPal account/mode — running it again just creates a
second product/plan, which is harmless but unnecessary.
"""
import os
import re
import sys
from pathlib import Path

import requests

SECRETS_PATH = Path(__file__).resolve().parent.parent / ".streamlit" / "secrets.toml"


def _read_secrets_toml() -> dict:
    if not SECRETS_PATH.exists():
        return {}
    try:
        import tomllib
    except ImportError:
        import tomli as tomllib
    with SECRETS_PATH.open("rb") as f:
        data = tomllib.load(f)
    return data.get("paypal", {})


_secrets = _read_secrets_toml()

client_id = os.environ.get("PAYPAL_CLIENT_ID") or _secrets.get("client_id")
client_secret = os.environ.get("PAYPAL_CLIENT_SECRET") or _secrets.get("client_secret")
if not client_id or not client_secret:
    sys.exit(
        "No PayPal credentials found. Either set PAYPAL_CLIENT_ID/PAYPAL_CLIENT_SECRET "
        "in your environment, or fill in client_id/client_secret under [paypal] in "
        ".streamlit/secrets.toml."
    )

mode = os.environ.get("PAYPAL_MODE") or _secrets.get("mode", "sandbox")
base_url = "https://api-m.paypal.com" if mode == "live" else "https://api-m.sandbox.paypal.com"

token_response = requests.post(
    f"{base_url}/v1/oauth2/token",
    auth=(client_id, client_secret),
    data={"grant_type": "client_credentials"},
    timeout=15,
)
token_response.raise_for_status()
access_token = token_response.json()["access_token"]
headers = {"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"}

product_response = requests.post(
    f"{base_url}/v1/catalogs/products",
    headers=headers,
    json={
        "name": "Ingestly — Premium",
        "type": "SERVICE",
        "category": "SOFTWARE",
    },
    timeout=15,
)
product_response.raise_for_status()
product_id = product_response.json()["id"]

plan_response = requests.post(
    f"{base_url}/v1/billing/plans",
    headers=headers,
    json={
        "product_id": product_id,
        "name": "Premium Monthly",
        "billing_cycles": [
            {
                "frequency": {"interval_unit": "MONTH", "interval_count": 1},
                "tenure_type": "REGULAR",
                "sequence": 1,
                "total_cycles": 0,
                "pricing_scheme": {"fixed_price": {"value": "19.00", "currency_code": "USD"}},
            }
        ],
        "payment_preferences": {
            "auto_bill_outstanding": True,
            "payment_failure_threshold": 3,
        },
    },
    timeout=15,
)
plan_response.raise_for_status()
plan_id = plan_response.json()["id"]

print(f"Product created ({mode}): {product_id}")
print(f"Plan created ({mode}):    {plan_id}")

if SECRETS_PATH.exists():
    text = SECRETS_PATH.read_text(encoding="utf-8")
    new_line = f'plan_id = "{plan_id}"'
    if re.search(r'(?m)^plan_id\s*=.*$', text):
        text = re.sub(r'(?m)^plan_id\s*=.*$', new_line, text, count=1)
    else:
        text = re.sub(r'(?m)^(\[paypal\]\s*)$', rf'\1\n{new_line}', text, count=1)
    SECRETS_PATH.write_text(text, encoding="utf-8")
    print()
    print(f"Wrote plan_id into {SECRETS_PATH} automatically.")
else:
    print()
    print("Add this to .streamlit/secrets.toml under [paypal]:")
    print(f'plan_id = "{plan_id}"')
