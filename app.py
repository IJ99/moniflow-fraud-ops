import streamlit as st
import pandas as pd
import numpy as np
import joblib
from datetime import datetime

st.set_page_config(page_title="Moniflow Fraud Risk Scorer", page_icon="🛡️", layout="wide")

# ── Load model artifacts ─────────────────────────────────────────
@st.cache_resource
def load_artifacts():
    model = joblib.load("model_v4.pkl")
    final_cols = joblib.load("final_cols_v4.pkl")
    txnType_freq_map = joblib.load("txnType_freq_map.pkl")
    txnPlatform_freq_map = joblib.load("txnPlatform_freq_map.pkl")
    customer_profile = joblib.load("customer_profile.pkl")
    known_ips = joblib.load("known_ips.pkl")
    known_recipients = joblib.load("known_recipients.pkl")
    customer_type_avgs = joblib.load("customer_type_avgs.pkl")
    return (model, final_cols, txnType_freq_map, txnPlatform_freq_map,
            customer_profile, known_ips, known_recipients, customer_type_avgs)

(model, final_cols, txnType_freq_map, txnPlatform_freq_map,
 customer_profile, known_ips, known_recipients, customer_type_avgs) = load_artifacts()

TIER_LIMITS = {1: 50_000, 2: 200_000, 3: 1_000_000, 4: 5_000_000}

# Approximate risk-tier cutoffs, derived from the historical score distribution
# (bottom 1% = High, next 4% = Medium). These are reference points from training,
# not recalculated live for every new batch.
HIGH_CUTOFF = 0.0
MEDIUM_CUTOFF = 0.0656

# ── Header ─────────────────────────────────────────
st.title("🛡️ Moniflow Fraud Risk Scorer")
st.caption("Isolation Forest model — scores transactions on behavior alone, never trained on the blacklist/PND label.")

st.warning(
    "**Not yet validated against confirmed outcomes.** The model hasn't been checked against a "
    "point-in-time-correct blacklist label — that data isn't available yet (missing blacklist/PND "
    "date field). Geolocation-based checks (impossible travel, new country) aren't available in this "
    "demo since it has no live GPS/IP-geolocation feed. Treat scores here as a demonstration of the "
    "engineering, not a certified accuracy claim.",
    icon="⚠️",
)

st.divider()

# ── Customer selection ─────────────────────────────────────────
col_left, col_right = st.columns([1, 1.4])

with col_left:
    st.subheader("1. Pick a real customer")
    referral_id = st.selectbox(
        "Customer (referralID)",
        options=sorted(customer_profile["referralID"].unique()),
        index=0,
    )

    profile_row = customer_profile[customer_profile["referralID"] == referral_id].iloc[0]
    signup_date = pd.to_datetime(profile_row["signupDate"])
    kyc_level = int(profile_row["kycLevel"]) if pd.notna(profile_row["kycLevel"]) else 1
    last_txn_period = pd.to_datetime(profile_row["last_txnPeriod"])
    last_24h_count = float(profile_row["last_txnCountLast24h"]) if pd.notna(profile_row["last_txnCountLast24h"]) else 0.0

    today = datetime.now()
    account_age_days = (today - signup_date).days

    known_ip_set = known_ips.get(referral_id, set())
    known_recipient_set = known_recipients.get(referral_id, set())

    st.markdown("**Real history on file for this customer**")
    m1, m2, m3 = st.columns(3)
    m1.metric("Account age (days)", account_age_days)
    m2.metric("KYC tier", kyc_level)
    m3.metric("Daily limit", f"₦{TIER_LIMITS.get(kyc_level, 0):,.0f}")
    st.caption(f"Signed up {signup_date.date()} · {len(known_ip_set)} known IP(s) · {len(known_recipient_set)} known recipient(s) · last activity {last_txn_period.date()}")

    st.subheader("2. Enter a new transaction")
    txn_type = st.selectbox("Transaction type", options=sorted(txnType_freq_map.index))
    txn_platform = st.selectbox("Platform", options=sorted(txnPlatform_freq_map.index))
    txn_amount = st.number_input("Amount (₦)", min_value=0.0, value=5000.0, step=1000.0)
    txn_ip = st.text_input("IP address for this transaction", value="102.91.77.1")

    is_transfer = "Transfer" in txn_type or "Deposit" in txn_type
    recipient_no = ""
    if is_transfer:
        recipient_no = st.text_input("Recipient account number (if a transfer)", value="")

    with st.expander("Advanced fields (fees, verification, velocity)"):
        txn_fee = st.number_input("Fee (₦)", min_value=0.0, value=0.0)
        discount = st.number_input("Discount (₦)", min_value=0.0, value=0.0)
        cashback = st.number_input("Cashback (₦)", min_value=0.0, value=0.0)
        is_cashback_used = st.checkbox("Cashback used on this transaction", value=False)
        txn_tries = st.number_input("Attempts before this succeeded", min_value=0, value=0, step=1)
        is_phone_verified = st.checkbox("Phone verified", value=True)
        is_email_verified = st.checkbox("Email verified", value=True)
        extra_recent_txns = st.slider(
            "Additional transactions by this customer in the last 24h (on top of their last known activity)",
            min_value=0, max_value=20, value=0,
        )

    run_it = st.button("Score this transaction", type="primary", use_container_width=True)

# ── Scoring ─────────────────────────────────────────
with col_right:
    st.subheader("3. Risk assessment")

    if run_it:
        # deviation from this customer's own average for this transaction type
        avg_for_type = customer_type_avgs.get((referral_id, txn_type))
        if avg_for_type and avg_for_type > 0:
            deviation = min(txn_amount / avg_for_type, 20.0)
            customer_avg_amount = avg_for_type
        else:
            deviation = 1.0
            customer_avg_amount = txn_amount

        # velocity: anchor to their last known 24h count + any extra entered
        txn_count_24h = last_24h_count + extra_recent_txns

        # new IP / multiple-IPs-on-new-account
        is_new_ip = txn_ip not in known_ip_set
        new_ip_high_value = int(is_new_ip and txn_amount > 100_000)
        distinct_ip_count = len(known_ip_set) + (1 if is_new_ip else 0)
        multiple_ips_new_account = int(account_age_days <= 7 and distinct_ip_count >= 2)

        # recipient history
        is_first_time_recipient = bool(recipient_no) and (recipient_no not in known_recipient_set)
        first_time_high_value = int(is_first_time_recipient and txn_amount > 200_000)
        first_time_recipient_new_account = int(is_first_time_recipient and account_age_days <= 7)

        # tier-aware daily amount (approximated to this single transaction —
        # a live system would sum today's real transactions)
        daily_limit = TIER_LIMITS.get(kyc_level, 50_000)
        high_daily_amount_flag = int(txn_amount > 0.8 * daily_limit)

        # new-account high value
        new_account_high_value = int(account_age_days <= 7 and txn_amount > 200_000)

        # not available in this demo — needs live geolocation
        impossible_travel = 0
        new_country_flag = 0

        row = {
            "txnAmount": txn_amount,
            "txnFee": txn_fee,
            "discount": discount,
            "cashback": cashback,
            "isCashbackUsed": int(is_cashback_used),
            "txnTries": txn_tries,
            "accountAgeDays": account_age_days,
            "kycLevel": kyc_level,
            "isPhoneVerified": int(is_phone_verified),
            "isEmailVerified": int(is_email_verified),
            "customerAvgAmountSoFar": customer_avg_amount,
            "deviationFromCustomerAvg": deviation,
            "txnCountLast24h": txn_count_24h,
            "txnType_freq": txnType_freq_map.get(txn_type, 0),
            "txnPlatform_freq": txnPlatform_freq_map.get(txn_platform, 0),
            "new_account_high_value": new_account_high_value,
            "impossible_travel": impossible_travel,
            "new_country_flag": new_country_flag,
            "high_daily_amount_flag": high_daily_amount_flag,
            "first_time_high_value": first_time_high_value,
            "new_ip_high_value": new_ip_high_value,
            "multiple_ips_new_account": multiple_ips_new_account,
            "first_time_recipient_new_account": first_time_recipient_new_account,
        }

        X = pd.DataFrame([row])[final_cols]
        score = float(model.decision_function(X)[0])
        raw_pred = model.predict(X)[0]

        if score <= HIGH_CUTOFF:
            tier, color = "HIGH", "red"
        elif score <= MEDIUM_CUTOFF:
            tier, color = "MEDIUM", "orange"
        else:
            tier, color = "LOW", "green"

        st.markdown(f"### Risk tier: :{color}[**{tier}**]")
        st.metric("Anomaly score", f"{score:.4f}", help="Lower = more anomalous. Isolation Forest's raw decision function output.")

        action = {
            "HIGH": "Block / send to compliance for review",
            "MEDIUM": "Hold for customer-care review",
            "LOW": "Pass through",
        }[tier]
        st.info(f"**Suggested action:** {action}")

        st.markdown("**What drove this score**")
        signals = []
        if deviation > 3:
            signals.append(f"Amount is {deviation:.1f}× this customer's usual spend on '{txn_type}'")
        if multiple_ips_new_account:
            signals.append("New account already using 2+ different IP addresses — strongest signal found in this project (85% hit rate on known fraud in testing)")
        if new_account_high_value:
            signals.append(f"New account (≤7 days) making a transaction over ₦200,000")
        if new_ip_high_value:
            signals.append("Unfamiliar IP address combined with a high amount")
        if first_time_recipient_new_account:
            signals.append("New account sending to a recipient never paid before")
        if high_daily_amount_flag:
            signals.append(f"Amount exceeds 80% of this customer's Tier {kyc_level} daily limit (₦{daily_limit:,.0f})")
        if txn_count_24h >= 5:
            signals.append(f"High transaction velocity ({txn_count_24h:.0f} in 24h)")

        if signals:
            for s in signals:
                st.markdown(f"- {s}")
        else:
            st.markdown("- No individual rule strongly triggered — score reflects the overall combination of features rather than one standout signal.")

        with st.expander("Full feature vector sent to the model"):
            st.dataframe(X.T.rename(columns={0: "value"}), use_container_width=True)
    else:
        st.markdown("Fill in a transaction on the left and click **Score this transaction**.")

st.divider()
st.caption(
    "Model: Isolation Forest, trained on Moniflow historical transactions (Jan 2023–Mar 2026), "
    "unsupervised — never trained on isBlacklisted/isPND. Risk tiers use approximate historical "
    "cutoffs (High: bottom 1% of scores, Medium: next 4%)."
)
