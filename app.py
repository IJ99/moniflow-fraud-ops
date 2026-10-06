import os
import textwrap
import joblib
import numpy as np
import pandas as pd
import streamlit as st

# -----------------------------------------------------------------------------
# 1. PAGE CONFIGURATION
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Moniflow RiskShield | Fraud Operations Portal",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

def render_html(html_str: str):
    """Safely renders HTML without triggering Markdown indented code block formatting."""
    cleaned_html = "\n".join([line.strip() for line in html_str.split("\n")])
    st.markdown(cleaned_html, unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# 2. ENTERPRISE SAAS PORTAL STYLING (MONIFLOW NAVY & BLUE THEME)
# -----------------------------------------------------------------------------
render_html(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background-color: #F4F7FB !important;
        color: #1E293B !important;
    }
    .stApp {
        background-color: #F4F7FB !important;
    }

    /* Hide Default Streamlit Chrome */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    .block-container {
        padding-top: 1.1rem !important;
        padding-bottom: 2.5rem !important;
        max-width: 1440px !important;
    }

    /* Force all Streamlit markdown and captions to dark text by default (beats dark mode) */
    .stMarkdown, .stMarkdown p, [data-testid="stMarkdownContainer"] p {
        color: #1E293B;
    }

    /* Top SaaS Navigation Bar */
    .mf-navbar {
        background: linear-gradient(135deg, #0E2A47 0%, #163A5F 100%);
        border-radius: 14px;
        padding: 16px 26px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 10px 25px -5px rgba(14, 42, 71, 0.22);
        margin-bottom: 18px;
        border-bottom: 3px solid #0077CC;
    }
    .mf-brand {
        display: flex;
        align-items: center;
        gap: 14px;
    }
    .mf-logo-box {
        width: 42px;
        height: 42px;
        background: linear-gradient(135deg, #0077CC 0%, #38BDF8 100%);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        box-shadow: 0 4px 12px rgba(0, 119, 204, 0.4);
    }
    .mf-title {
        color: #FFFFFF !important;
        font-size: 19px;
        font-weight: 800;
        letter-spacing: -0.3px;
        margin: 0;
        line-height: 1.2;
    }
    .mf-subtitle {
        color: #93C5FD !important;
        font-size: 12px;
        font-weight: 500;
        margin: 2px 0 0 0;
    }
    .mf-nav-badges {
        display: flex;
        align-items: center;
        gap: 10px;
        flex-wrap: wrap;
    }
    .mf-pill-live {
        background: rgba(16, 185, 129, 0.18);
        border: 1px solid rgba(16, 185, 129, 0.45);
        color: #6EE7B7 !important;
        padding: 5px 12px;
        border-radius: 999px;
        font-size: 12px;
        font-weight: 700;
    }

    /* Style the Text Input Box */
    div[data-baseweb="input"] {
        background-color: #FFFFFF !important;
        border: 1.8px solid #0077CC !important;
        border-radius: 8px !important;
        height: 42px !important;
    }
    div[data-baseweb="input"] input {
        color: #0E2A47 !important;
        font-weight: 700 !important;
        font-family: 'JetBrains Mono', monospace !important;
        font-size: 15px !important;
        background-color: #FFFFFF !important;
        -webkit-text-fill-color: #0E2A47 !important;
    }

    /* Card Styling */
    .mf-card {
        background: #FFFFFF;
        border: 1px solid #DCE6F2;
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 4px 14px rgba(14, 42, 71, 0.04);
        box-sizing: border-box;
    }
    .mf-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        border-bottom: 1px solid #EEF2F6;
        padding-bottom: 12px;
        margin-bottom: 14px;
    }
    .mf-card-title {
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: #0077CC !important;
        margin: 0;
    }
    .mf-card-badge {
        font-size: 11px;
        font-weight: 700;
        padding: 3px 9px;
        border-radius: 6px;
        background: #EBF5FF;
        color: #0E2A47 !important;
        font-family: 'JetBrains Mono', monospace;
    }

    /* Customer Profile Styling */
    .mf-user-hero {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 12px;
        padding: 10px 12px;
        background: #F8FAFC;
        border-radius: 10px;
        border: 1px solid #E2E8F0;
    }
    .mf-avatar {
        width: 42px;
        height: 42px;
        border-radius: 50%;
        background: linear-gradient(135deg, #0E2A47 0%, #0077CC 100%);
        color: #FFFFFF !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 16px;
        flex-shrink: 0;
    }
    .mf-username {
        font-size: 17px;
        font-weight: 800;
        color: #0E2A47 !important;
        margin: 0;
    }
    .mf-user-sub {
        font-size: 11.5px;
        color: #64748B !important;
        margin: 2px 0 0 0;
    }

    /* Key-Value Grid Boxes */
    .mf-kv-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
        margin-bottom: 12px;
    }
    .mf-kv-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 8px 10px;
    }
    .mf-kv-label {
        font-size: 10px;
        font-weight: 700;
        color: #64748B !important;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        margin-bottom: 3px;
    }
    .mf-kv-val {
        font-size: 14px;
        font-weight: 700;
        color: #0F172A !important;
        font-family: 'JetBrains Mono', monospace;
    }
    .mf-kv-sub {
        font-size: 10.5px;
        color: #64748B !important;
        margin-top: 2px;
    }

    /* Transaction Amount Banner */
    .mf-amount-hero {
        background: linear-gradient(135deg, #EBF5FF 0%, #F0F9FF 100%);
        border: 1px solid #BAE6FD;
        border-radius: 10px;
        padding: 12px 14px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .mf-amount-val {
        font-size: 24px;
        font-weight: 800;
        color: #0E2A47 !important;
        font-family: 'JetBrains Mono', monospace;
        margin: 0;
    }
    .mf-type-pill {
        background: #0E2A47;
        color: #FFFFFF !important;
        padding: 5px 11px;
        border-radius: 7px;
        font-size: 11.5px;
        font-weight: 700;
    }

    /* Bottom Footer Box inside Cards */
    .mf-card-footer-box {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        padding: 9px 11px;
    }

    /* Risk Decision Card */
    .mf-risk-box {
        border-radius: 10px;
        padding: 16px 14px;
        text-align: center;
        margin-bottom: 12px;
        flex-grow: 1;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }
    .mf-risk-low {
        background: #ECFDF5;
        border: 2px solid #10B981;
        color: #065F46 !important;
    }
    .mf-risk-med {
        background: #FFFBEB;
        border: 2px solid #F59E0B;
        color: #92400E !important;
    }
    .mf-risk-high {
        background: #FEF2F2;
        border: 2px solid #EF4444;
        color: #991B1B !important;
    }
    .mf-prob-big {
        font-size: 42px;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        line-height: 1.1;
        margin: 8px 0;
    }
    .mf-meter-track {
        width: 100%;
        height: 9px;
        background: #E2E8F0;
        border-radius: 999px;
        overflow: hidden;
        margin: 10px 0 6px 0;
    }
    .mf-action-banner {
        padding: 10px 12px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 12px;
        text-align: center;
    }

    /* SHAP Factor Cards */
    .mf-shap-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 12px;
    }
    .mf-shap-card {
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 11px;
        padding: 13px 15px;
        display: flex;
        align-items: flex-start;
        justify-content: space-between;
        gap: 12px;
    }
    .mf-shap-feat {
        font-size: 13px;
        font-weight: 800;
        color: #0E2A47 !important;
        margin: 0 0 3px 0;
        font-family: 'JetBrains Mono', monospace;
    }
    .mf-shap-val {
        font-size: 12px;
        font-weight: 600;
        color: #0077CC !important;
        margin-bottom: 3px;
    }
    .mf-shap-desc {
        font-size: 11.5px;
        color: #64748B !important;
        margin: 0;
        line-height: 1.35;
    }
    .mf-shap-pos {
        background: #FEE2E2;
        color: #B91C1C !important;
        border: 1px solid #FCA5A5;
        padding: 4px 9px;
        border-radius: 6px;
        font-size: 11.5px;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        white-space: nowrap;
    }
    .mf-shap-neg {
        background: #D1FAE5;
        color: #047857 !important;
        border: 1px solid #6EE7B7;
        padding: 4px 9px;
        border-radius: 6px;
        font-size: 11.5px;
        font-weight: 800;
        font-family: 'JetBrains Mono', monospace;
        white-space: nowrap;
    }
    </style>
    """
)

# -----------------------------------------------------------------------------
# 3. FEATURE DESCRIPTIONS FOR COMPLIANCE ANALYSTS
# -----------------------------------------------------------------------------
FEATURE_INFO = {
    "txnAmount": ("Transaction Amount", "The Naira size of the transaction being attempted."),
    "txnFee": ("Transaction Fee", "Service fee charged on this transaction."),
    "discount": ("Promotional Discount", "Discount value applied to this purchase."),
    "isCashbackUsed": ("Cashback Toggle", "Whether the customer funded this transaction using free promo/cashback balance (1 = Yes, 0 = No)."),
    "cashback": ("Cashback Earned", "Amount of new cashback reward earned on this transaction."),
    "accountAgeDays": ("Account Age (Days)", "Days elapsed between account signup and this transaction."),
    "accountStatus": ("Account Status", "Whether the account is active (1) or restricted (0) at transaction time."),
    "customerAvgAmountSoFar": ("Personal Type Average", "Customer's historical average spend for this specific transaction type."),
    "deviationFromCustomerAvg": ("Jump From Average", "Ratio comparing this transaction amount against the customer's personal average."),
    "txnCountLast24h": ("24h Txn Velocity", "Number of transactions initiated by this user in the preceding 24 hours."),
    "coordinated_signup_flag_v2": ("72h Shared Signup IP Cluster", "Number of other accounts registered on the same primary IP within 72 hours."),
    "cumulativeSpend24h": ("24h Cumulative Spend", "Total Naira volume moved by this user in the preceding 24 hours (structuring check)."),
    "is_first_time_dest_bank": ("First-Time Destination Bank", "Whether this is the user's very first transfer to this bank (1 = Yes, 0 = No)."),
    "impossible_travel_flag": ("Impossible Travel Check", "Whether user GPS jumped across cities faster than >900 km/h (1 = Yes, 0 = No)."),
}

KYC_LIMITS = {1: 50_000, 2: 200_000, 3: 5_000_000}

# -----------------------------------------------------------------------------
# 4. LOAD MODEL & DATASET ARTIFACTS (OPTIMIZED O(1) LOOKUP & CACHED SHAP)
# -----------------------------------------------------------------------------
@st.cache_resource
def load_artifacts():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.join(base_dir, "Cleaned_transactions_new.csv")
    model_path = os.path.join(base_dir, "xgb_model_behavioral.pkl")
    cols_path = os.path.join(base_dir, "final_cols_behavioral.pkl")

    # 1. Load the dataset
    df = pd.read_csv(csv_path)
    
    # [OPTIMIZATION] Set txnId as the index for instant mathematical lookups
    if "txnId" in df.columns:
        df.set_index("txnId", inplace=True)

    # 2. Load model and columns
    model = joblib.load(model_path)
    final_cols = joblib.load(cols_path)

    # 3. Create dictionaries for fast set lookups
    valid_ips = df[df["txnIPAddress"].notna() & (df["txnIPAddress"] != "UNKNOWN")]
    known_ips = valid_ips.groupby("referralID")["txnIPAddress"].apply(set).to_dict()

    if "transferAccountNo" in df.columns:
        valid_recs = df[df["transferAccountNo"].notna()]
        known_recipients = valid_recs.groupby("referralID")["transferAccountNo"].apply(set).to_dict()
    else:
        known_recipients = {}
        
    # [OPTIMIZATION] Pre-build the heavy mathematical Explainer once and hold in RAM
    try:
        import shap
        explainer = shap.TreeExplainer(model)
    except Exception:
        explainer = None

    return df, model, final_cols, known_ips, known_recipients, explainer

try:
    df, model, final_cols, known_ips, known_recipients, explainer = load_artifacts()
except Exception as e:
    st.error(f"Error loading model or dataset artifacts: {e}")
    st.stop()

# -----------------------------------------------------------------------------
# 5. TOP SAAS NAVIGATION HEADER
# -----------------------------------------------------------------------------
render_html(
    f"""
    <div class="mf-navbar">
        <div class="mf-brand">
            <div class="mf-logo-box">🛡️</div>
            <div>
                <p class="mf-title">Moniflow RiskShield™ · Real-Time Fraud Operations Portal</p>
                <p class="mf-subtitle">Point-in-Time Behavioral XGBoost Engine · Calibrated on Unseen Accounts</p>
            </div>
        </div>
        <div class="mf-nav-badges">
            <span class="mf-pill-live">● ENGINE ONLINE</span>
        </div>
    </div>
    """
)

# -----------------------------------------------------------------------------
# 6. TRANSACTION COMMAND BAR (CLEANED UP SEARCH ONLY)
# -----------------------------------------------------------------------------
# 1. Set the default starting ID in memory only if it doesn't exist yet
if "search_txn_id" not in st.session_state:
    st.session_state.search_txn_id = "261268"

render_html('<div style="color: #0077CC !important; font-weight: 800; font-size: 11px; text-transform: uppercase; letter-spacing: 0.5px; margin-bottom: 6px; white-space: nowrap;">🔍 TRANSACTION TELEMETRY LOOKUP (TXNID)</div>')

# 2. Use 'key' to automatically link the input box to Streamlit's memory without fighting the browser
txn_input = st.text_input(
    "Transaction ID",
    key="search_txn_id",
    placeholder="e.g. 261268, 83124, 263519...",
    label_visibility="collapsed",
)

render_html("<div style='height: 10px;'></div>")

# -----------------------------------------------------------------------------
# 7. LOOKUP & SCORE TRANSACTION (O(1) FAST LOOKUP)
# -----------------------------------------------------------------------------
if txn_input.strip():
    try:
        tid = int(txn_input.strip())
    except ValueError:
        st.warning("Please enter a valid numeric Transaction ID (txnId).")
        st.stop()

    # [OPTIMIZATION] Search instantly by index instead of scanning columns
    if tid not in df.index:
        st.warning(f"No transaction found with txnId = {tid} in the master dataset.")
        st.stop()

    # Retrieve the exact row instantly
    row = df.loc[tid]
    if isinstance(row, pd.DataFrame): 
        row = row.iloc[0] # Just in case duplicate IDs exist

    user_id = str(row.get("referralID", "UNKNOWN"))
    acct_age = int(row.get("accountAgeDays", 0))
    acct_status = int(row.get("accountStatus", 1))
    kyc_tier = int(row.get("kycLevel", 1)) if pd.notna(row.get("kycLevel", 1)) else 1
    daily_limit = KYC_LIMITS.get(kyc_tier, 50_000)

    n_ips = len(known_ips.get(user_id, set()))
    n_recs = len(known_recipients.get(user_id, set()))

    amt = float(row.get("txnAmount", 0.0))
    fee = float(row.get("txnFee", 0.0))
    disc = float(row.get("discount", 0.0))
    cb_used = int(row.get("isCashbackUsed", 0))
    cb_earned = float(row.get("cashback", 0.0))
    cust_avg = float(row.get("customerAvgAmountSoFar", amt))
    dev_ratio = float(row.get("deviationFromCustomerAvg", 1.0))
    spend_24h = float(row.get("cumulativeSpend24h", 0.0))
    count_24h = int(row.get("txnCountLast24h", 0))
    txn_type = str(row.get("txnType", "N/A"))
    platform = str(row.get("txnPlatform", "N/A"))
    ip_addr = str(row.get("txnIPAddress", "UNKNOWN"))
    cluster_size = int(row.get("coordinated_signup_flag_v2", 0))
    recipient = row.get("transferAccountNo", None)
    recipient_str = str(recipient) if pd.notna(recipient) and str(recipient).strip() != "" else "Internal / Utility"
    first_bank = int(row.get("is_first_time_dest_bank", 0))
    imp_travel = int(row.get("impossible_travel_flag", 0))
    txn_time = str(row.get("txnPeriod", "N/A"))

    # Predict Fraud Risk Probability
    X_input = pd.DataFrame([row[final_cols]])[final_cols].astype(float)
    prob = float(model.predict_proba(X_input)[0][1])
    prob_pct = prob * 100.0

    if prob >= 0.95:
        risk_tier = "HIGH RISK"
        risk_cls = "mf-risk-high"
        bar_color = "#EF4444"
        action_text = "🚫 AUTO-BLOCK & ALERT COMPLIANCE"
        action_bg = "#FEE2E2"
        action_color = "#991B1B"
    elif prob >= 0.50:
        risk_tier = "MEDIUM RISK"
        risk_cls = "mf-risk-med"
        bar_color = "#F59E0B"
        action_text = "⚠️ HOLD FOR COMPLIANCE REVIEW QUEUE"
        action_bg = "#FEF3C7"
        action_color = "#92400E"
    else:
        risk_tier = "LOW RISK"
        risk_cls = "mf-risk-low"
        bar_color = "#10B981"
        action_text = "✅ PASS THROUGH INSTANTLY"
        action_bg = "#D1FAE5"
        action_color = "#065F46"

    # Daily limit utilization percentage
    limit_pct = min(100.0, (spend_24h / daily_limit) * 100.0) if daily_limit > 0 else 0.0

    # -------------------------------------------------------------------------
    # 8. THREE EQUAL-SIZED CARDS USING CSS GRID (PERFECT EQUAL WIDTH & HEIGHT)
    # -------------------------------------------------------------------------
    initials = user_id[:2].upper() if len(user_id) >= 2 else "MF"
    status_badge = "🟢 ACTIVE" if acct_status == 1 else "🔴 RESTRICTED"
    cluster_badge = f"⚠️ {cluster_size} Other Accts (Gang Risk)" if cluster_size >= 5 else f"🟢 {cluster_size} Other Accts (Normal)"
    first_bank_str = "⚠️ First-Time Bank (1)" if first_bank == 1 else "🟢 Known Bank (0)"
    travel_str = "🚨 Impossible Jump (1)" if imp_travel == 1 else "🟢 Normal GPS (0)"
    cb_str = "Yes (1)" if cb_used == 1 else "No (0)"
    bar_width = max(2.0, min(100.0, prob_pct))

    three_cards_html = f"""
    <div style="display: grid; grid-template-columns: repeat(3, minmax(0, 1fr)); gap: 18px; align-items: stretch; margin-bottom: 18px;">
        
        <!-- CARD 1: CUSTOMER PROFILE & KYC -->
        <div class="mf-card" style="margin: 0; display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
            <div>
                <div class="mf-card-header">
                    <p class="mf-card-title">👤 Customer Identity & KYC</p>
                    <span class="mf-card-badge">{status_badge}</span>
                </div>
                <div class="mf-user-hero">
                    <div class="mf-avatar">{initials}</div>
                    <div>
                        <p class="mf-username">{user_id}</p>
                        <p class="mf-user-sub">Referral Handle · KYC Tier {kyc_tier}</p>
                    </div>
                </div>
                <div class="mf-kv-grid">
                    <div class="mf-kv-box">
                        <div class="mf-kv-label">Account Age at Txn</div>
                        <div class="mf-kv-val">{acct_age:,} days</div>
                        <div class="mf-kv-sub">{'⚠️ New Signup (<3d)' if acct_age <= 2 else 'Established Account'}</div>
                    </div>
                    <div class="mf-kv-box">
                        <div class="mf-kv-label">KYC Daily Limit</div>
                        <div class="mf-kv-val">₦{daily_limit:,.0f}</div>
                        <div class="mf-kv-sub">Tier {kyc_tier} Threshold</div>
                    </div>
                    <div class="mf-kv-box">
                        <div class="mf-kv-label">Known IP Footprint</div>
                        <div class="mf-kv-val">{n_ips:,} IP(s)</div>
                        <div class="mf-kv-sub">Historical Network IDs</div>
                    </div>
                    <div class="mf-kv-box">
                        <div class="mf-kv-label">Known Recipients</div>
                        <div class="mf-kv-val">{n_recs:,} Acct(s)</div>
                        <div class="mf-kv-sub">Saved Beneficiaries</div>
                    </div>
                </div>
            </div>
            <div class="mf-card-footer-box">
                <div style="display:flex; justify-content:space-between; font-size:11px; font-weight:700; color:#64748B; margin-bottom:5px;">
                    <span>24H LIMIT UTILIZATION</span>
                    <span style="color:#0E2A47;">{limit_pct:.1f}% (₦{spend_24h:,.0f} / ₦{daily_limit:,.0f})</span>
                </div>
                <div style="width:100%; height:8px; background:#E2E8F0; border-radius:999px; overflow:hidden;">
                    <div style="width:{limit_pct}%; height:100%; background:#0077CC; border-radius:999px;"></div>
                </div>
            </div>
        </div>

        <!-- CARD 2: LIVE TRANSACTION TELEMETRY -->
        <div class="mf-card" style="margin: 0; display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
            <div>
                <div class="mf-card-header">
                    <p class="mf-card-title">📝 Transaction Telemetry</p>
                    <span class="mf-card-badge">ID #{tid} · {txn_time}</span>
                </div>
                <div class="mf-amount-hero">
                    <div>
                        <div style="font-size:10px; font-weight:700; color:#0077CC; text-transform:uppercase;">Attempted Value (Fee: ₦{fee:,.2f})</div>
                        <p class="mf-amount-val">₦{amt:,.2f}</p>
                    </div>
                    <span class="mf-type-pill">{txn_type} · {platform}</span>
                </div>
                <div class="mf-kv-grid">
                    <div class="mf-kv-box">
                        <div class="mf-kv-label">Personal Avg (This Type)</div>
                        <div class="mf-kv-val">₦{cust_avg:,.2f}</div>
                        <div class="mf-kv-sub">Deviation: <b>{dev_ratio:.2f}x</b> usual</div>
                    </div>
                    <div class="mf-kv-box">
                        <div class="mf-kv-label">Prior 24h Spend & Speed</div>
                        <div class="mf-kv-val">₦{spend_24h:,.2f}</div>
                        <div class="mf-kv-sub">Across <b>{count_24h}</b> prior txn(s) in 24h</div>
                    </div>
                    <div class="mf-kv-box">
                        <div class="mf-kv-label">Origin IP & 72h Cluster</div>
                        <div class="mf-kv-val" style="font-size:12.5px;">{ip_addr}</div>
                        <div class="mf-kv-sub">{cluster_badge}</div>
                    </div>
                    <div class="mf-kv-box">
                        <div class="mf-kv-label">Destination & Security</div>
                        <div class="mf-kv-val" style="font-size:12.5px;">{recipient_str}</div>
                        <div class="mf-kv-sub">{first_bank_str} · {travel_str}</div>
                    </div>
                </div>
            </div>
            <div class="mf-card-footer-box" style="display:flex; justify-content:space-between; align-items:center; font-size:11px; color:#0E2A47; font-weight:600;">
                <span>💳 Cashback Used: <b>{cb_str}</b></span>
                <span>🎁 Earned: <b>₦{cb_earned:,.2f}</b></span>
                <span>🏷️️ Disc: <b>₦{disc:,.2f}</b></span>
            </div>
        </div>

        <!-- CARD 3: REAL-TIME RISK VERDICT -->
        <div class="mf-card" style="margin: 0; display: flex; flex-direction: column; justify-content: space-between; height: 100%;">
            <div>
                <div class="mf-card-header">
                    <p class="mf-card-title">🛡 Real-Time Risk Verdict</p>
                    <span class="mf-card-badge">XGBoost · 150 Trees</span>
                </div>
                <div class="mf-risk-box {risk_cls}">
                    <div style="font-size:11.5px; font-weight:800; letter-spacing:1px; text-transform:uppercase;">{risk_tier}</div>
                    <div class="mf-prob-big">{prob_pct:.2f}%</div>
                    <div style="font-size:11px; opacity:0.85;">Point-in-Time Fraud Probability</div>
                    <div class="mf-meter-track">
                        <div style="width:{bar_width}%; height:100%; background:{bar_color}; border-radius:999px;"></div>
                    </div>
                    <div style="display:flex; justify-content:space-between; font-size:9.5px; font-weight:700; opacity:0.75;">
                        <span>0% SAFE</span>
                        <span>50% REVIEW</span>
                        <span>95% BLOCK</span>
                    </div>
                </div>
            </div>
            <div>
                <div class="mf-action-banner" style="background:{action_bg}; color:{action_color}; border:1px solid {bar_color};">
                    {action_text}
                </div>
                <div style="margin-top:8px; font-size:10.5px; color:#64748B; text-align:center;">
                    Evaluated across <b>14 behavioral rules</b> with zero static blacklist leakage.
                </div>
            </div>
        </div>

    </div>
    """
    render_html(three_cards_html)

    # -------------------------------------------------------------------------
    # 9. SHAP EXPLAINABILITY ENGINE (VISUAL CARDS)
    # -------------------------------------------------------------------------
    if explainer is not None:
        try:
            sv = explainer.shap_values(X_input)
            if isinstance(sv, list):
                sv_row = sv[1][0]
            elif hasattr(sv, "values"):
                sv_row = sv.values[0]
            else:
                sv_row = sv[0]

            shap_df = pd.DataFrame(
                {
                    "feature": final_cols,
                    "value": X_input.iloc[0].values,
                    "shap": sv_row,
                }
            )

            if prob >= 0.50:
                header_note = "Top 4 Behavioral Clues Pushing This Transaction Toward FRAUD (+ Suspicion)"
                filtered = shap_df[shap_df["shap"] > 0].sort_values("shap", ascending=False)
                if filtered.empty:
                    filtered = shap_df.reindex(shap_df["shap"].abs().sort_values(ascending=False).index)
            else:
                header_note = "Top 4 Behavioral Clues Keeping This Transaction in the SAFE Zone (- Suspicion)"
                filtered = shap_df[shap_df["shap"] < 0].sort_values("shap", ascending=True)
                if filtered.empty:
                    filtered = shap_df.reindex(shap_df["shap"].abs().sort_values(ascending=False).index)

            top4 = filtered.head(4)

            cards_html = ""
            for _, srow in top4.iterrows():
                fname = srow["feature"]
                fval = srow["value"]
                fshap = srow["shap"]
                friendly_title, desc = FEATURE_INFO.get(fname, (fname, "Behavioral risk factor."))

                if fname in ["txnAmount", "txnFee", "discount", "cashback", "customerAvgAmountSoFar", "cumulativeSpend24h"]:
                    val_str = f"₦{fval:,.2f}"
                elif fname == "deviationFromCustomerAvg":
                    val_str = f"{fval:.2f}x"
                else:
                    val_str = f"{fval:,.0f}"

                badge_cls = "mf-shap-pos" if fshap > 0 else "mf-shap-neg"
                sign_str = f"+{fshap:.2f} Risk" if fshap > 0 else f"{fshap:.2f} Safe"

                cards_html += f"""
                <div class="mf-shap-card">
                    <div>
                        <p class="mf-shap-feat">{friendly_title} <span style="font-weight:500; color:#64748B;">({fname})</span></p>
                        <div class="mf-shap-val">Observed Value: {val_str}</div>
                        <p class="mf-shap-desc">{desc}</p>
                    </div>
                    <div class="{badge_cls}">SHAP: {sign_str}</div>
                </div>
                """

            shap_section_html = f"""
            <div class="mf-card">
                <div class="mf-card-header">
                    <p class="mf-card-title">🔍 AI Decision Explainability (SHAP Behavioral Breakdown)</p>
                    <span class="mf-card-badge">{header_note}</span>
                </div>
                <div class="mf-shap-grid">
                    {cards_html}
                </div>
            </div>
            """
            render_html(shap_section_html)
        except Exception as e:
            st.info(f"SHAP explanation unavailable: {e}")

    # -------------------------------------------------------------------------
    # 10. RAW 14-FEATURE INSPECTOR (FOR AUDIT & CSV EXPORT)
    # -------------------------------------------------------------------------
    with st.expander("📋 Inspect Full 14-Feature Behavioral Vector (Audit & Export)"):
        vec_series = pd.Series(X_input.iloc[0].values, index=final_cols, name="value")
        st.dataframe(vec_series, use_container_width=True)