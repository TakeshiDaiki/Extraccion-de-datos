"""One-off helper: creates the "Premium" product and its $19/month recurring
billing plan in your PayPal account (sandbox by default), then prints the
plan ID to paste into .streamlit/secrets.toml.

Usage (from the repo root, with your virtualenv active):
    PAYPAL_CLIENT_ID=... PAYPAL_CLIENT_SECRET=... python scripts/setup_paypal_plan.py

Set PAYPAL_MODE=live to create it against the live PayPal API instead of
sandbox. Run this once per PayPal account/mode — running it again just
creates a second product/plan, which is harmless but unnecessary.
"""
import os
import sys

import requests

client_id = os.environ.get("PAYPAL_CLIENT_ID")
client_secret = os.environ.get("PAYPAL_CLIENT_SECRET")
if not client_id or not client_secret:
    sys.exit("Set PAYPAL_CLIENT_ID and PAYPAL_CLIENT_SECRET in your environment before running this script.")

mode = os.environ.get("PAYPAL_MODE", "sandbox")
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
        "name": "Master Data Explorer Pro — Premium",
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
print()
print("Add this to .streamlit/secrets.toml under [paypal]:")
print(f'plan_id = "{plan_id}"')
