import streamlit as st

from auth.guard import require_login, current_plan
from auth.service import set_plan, PLAN_LIMITS
from views._style import render_header

require_login()
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
                set_plan(st.session_state["user_email"], "free")
                st.rerun()

with col_premium:
    premium = PLAN_LIMITS["premium"]
    with st.container(border=True):
        st.markdown("#### ⭐ Premium — $19/month")
        st.write(f"Up to {premium['max_records']:,} records per extraction")
        st.write("All 6 sources + automation rules + Excel export")
        if plan["name"] == "premium":
            st.success("Current plan")
        else:
            if st.button("⭐ Upgrade to Premium", use_container_width=True, type="primary"):
                set_plan(st.session_state["user_email"], "premium")
                st.rerun()

st.markdown("---")
st.markdown('<div class="section-title">Billing — how this works</div>', unsafe_allow_html=True)
st.warning(
    "🚧 **No payment processor is connected yet.** Clicking \"Upgrade\" above only flips a "
    "flag in the database for demo purposes — no card is charged, and no money moves."
)
st.write(
    "Once billing goes live, here's how it's designed to work:"
)
st.write(
    "- **Processor:** payments would run through **Stripe**, a PCI-compliant payment "
    "processor used by most SaaS products — we would never store your card details "
    "ourselves.\n"
    "- **Accepted methods:** major credit and debit cards (Visa, Mastercard, American "
    "Express) via Stripe Checkout, the same flow used by thousands of subscription "
    "products.\n"
    "- **Where the money goes:** Stripe deposits subscription revenue into the "
    "connected business bank account on a regular payout schedule, after deducting its "
    "processing fee.\n"
    "- **Cancel anytime:** subscriptions would be self-service — downgrade back to Free "
    "whenever you want, no support ticket required."
)
