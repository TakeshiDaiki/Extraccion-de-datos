import streamlit as st

from auth.guard import require_login, current_plan
from auth.service import set_plan, get_subscription_id, PLAN_LIMITS
from billing import paypal_service
from views._style import render_header


def _clear_pending_checkout():
    st.session_state.pop("pending_paypal_subscription_id", None)
    st.session_state.pop("paypal_approve_url", None)


# Handle the redirect back from PayPal BEFORE requiring login. The browser
# leaves our app entirely to approve on PayPal's domain — that always tears
# down Streamlit's in-memory session (even when it's the same tab), so by the
# time we're back the user isn't logged in yet as far as this page knows. The
# subscriber's email travels in our own return_url (set at checkout time in
# billing/paypal_service.py, not something PayPal can alter) so we can still
# verify and record the subscription without a live session. We still verify
# server-side with PayPal (not trusting the redirect alone) so hitting this
# URL without actually approving can't grant Premium.
came_back_from_paypal = st.query_params.get("paypal_return") == "1"
if came_back_from_paypal:
    subscription_id = st.query_params.get("subscription_id")
    return_email = st.query_params.get("email")
    st.query_params.clear()
    _clear_pending_checkout()
    if subscription_id and return_email:
        ok, message = paypal_service.verify_subscription(subscription_id, return_email)
        if ok:
            set_plan(return_email, "premium", subscription_id=subscription_id)
            st.success("🎉 Payment confirmed! Log in to see your Premium plan.")
        else:
            st.error(f"We couldn't confirm your subscription: {message}")
    else:
        st.error("Missing checkout details — please try upgrading again.")
    st.page_link("views/login.py", label="Go to Login", icon="🔑")
    st.stop()
elif st.query_params.get("checkout") == "canceled":
    st.query_params.clear()
    _clear_pending_checkout()
    st.info("Checkout canceled — you're still on your current plan.")
    st.page_link("views/login.py", label="Go to Login", icon="🔑")
    st.stop()

require_login()
user_email = st.session_state["user_email"]
plan = current_plan()

render_header("Your Plan", icon="⭐")
st.info(f"Current plan: **{plan['label']}**")

st.markdown("---")
col_free, col_premium = st.columns(2)

with col_free:
    free = PLAN_LIMITS["free"]
    with st.container(border=True):
        st.markdown("#### Free — $0/month")
        st.write(f"Up to {free['max_records']} records per extraction")
        st.write(f"Sources: {', '.join(s.upper() for s in free['sources'])}")
        if plan["name"] == "free":
            st.success("Current plan")
        else:
            if st.button("Switch back to Free", use_container_width=True):
                subscription_id = get_subscription_id(user_email)
                if subscription_id:
                    try:
                        paypal_service.cancel_subscription(subscription_id)
                    except Exception as exc:
                        st.error(f"Couldn't cancel your PayPal subscription: {exc}")
                        st.stop()
                set_plan(user_email, "free")
                _clear_pending_checkout()
                st.rerun()

with col_premium:
    premium = PLAN_LIMITS["premium"]
    with st.container(border=True):
        st.markdown("#### ⭐ Premium — $19/month")
        st.write(f"Up to {premium['max_records']:,} records per extraction")
        st.write("All 6 sources + automation rules + Excel export")
        if plan["name"] == "premium":
            st.success("Current plan")
        elif paypal_service.is_configured():
            try:
                if "paypal_approve_url" not in st.session_state:
                    subscription_id, approve_url = paypal_service.create_subscription(user_email)
                    st.session_state["pending_paypal_subscription_id"] = subscription_id
                    st.session_state["paypal_approve_url"] = approve_url
                st.link_button(
                    "⭐ Upgrade to Premium",
                    st.session_state["paypal_approve_url"],
                    use_container_width=True,
                    type="primary",
                )
            except Exception as exc:
                st.error(f"Couldn't start checkout: {exc}")
        else:
            if st.button(
                "⭐ Upgrade to Premium (demo — PayPal not configured)",
                use_container_width=True,
                type="primary",
            ):
                set_plan(user_email, "premium")
                st.rerun()

st.markdown("---")
st.markdown('<div class="section-title">Billing — how this works</div>', unsafe_allow_html=True)
if paypal_service.is_configured():
    st.success(
        "✅ **PayPal is connected (sandbox mode).** Upgrading opens a real PayPal "
        "subscription approval flow — log in with a "
        "[PayPal sandbox test buyer account](https://developer.paypal.com/dashboard/accounts) "
        "to approve it. No real charge is made in sandbox mode."
    )
else:
    st.warning(
        "🚧 **No payment processor is connected yet.** Clicking \"Upgrade\" above only flips a "
        "flag in the database for demo purposes — no card is charged, and no money moves."
    )
st.write(
    "- **Processor:** payments run through **PayPal**, one of the most widely used "
    "payment platforms in the world — we never store your card or bank details "
    "ourselves.\n"
    "- **Accepted methods:** your PayPal balance, linked bank account, or linked "
    "card — whatever your PayPal account is set up to use.\n"
    "- **Where the money goes:** PayPal deposits subscription revenue into the "
    "connected business account, available for withdrawal to a linked bank account.\n"
    "- **Cancel anytime:** subscriptions are self-service — downgrading to Free above "
    "cancels the PayPal subscription immediately, no support ticket required."
)
