import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Subscription Health Monitor", 
                   layout="wide", page_icon="📊")

# Load all data
@st.cache_data
def load_data():
    subs = pd.read_csv('data/subscriptions_scored.csv')
    mrr = pd.read_csv('data/mrr_monthly.csv')
    health = pd.read_csv('data/health_scores.csv')
    outlier = pd.read_csv('data/outliers.csv')
    at_risk = None
    try:
        at_risk = pd.read_csv('data/at_risk_customers.csv')
    except FileNotFoundError:
        at_risk = None
    return subs, mrr, health, outlier, at_risk

subs, mrr, health, outlier, at_risk_file = load_data()

# Sidebar navigation
page = st.sidebar.selectbox("Navigate", [
    "📈 MRR Overview",
    "❤️ Customer Health",
    "🔍 Outlier Detection",
    "⚠️ Churn Prediction"
])

# ── PAGE 1 ──────────────────────────────────────────
if page == "📈 MRR Overview":
    st.title("📈 MRR Overview")

    col1, col2, col3 = st.columns(3)
    col1.metric("Total MRR",      f"${subs[subs.status=='active']['mrr'].sum():,.0f}")
    col2.metric("Active Customers", len(subs[subs.status=='active']))
    col3.metric("Churned Customers", len(subs[subs.status=='churned']))

    st.subheader("Monthly MRR Growth")
    fig, ax = plt.subplots(figsize=(10,4))
    ax.plot(mrr['month'], mrr['total_mrr'], marker='o', color='steelblue')
    ax.set_xlabel("Month")
    ax.set_ylabel("MRR ($)")
    ax.tick_params(axis='x', rotation=45)
    st.pyplot(fig)

    st.subheader("MRR Table")
    st.dataframe(mrr, width='stretch')

# ── PAGE 2 ──────────────────────────────────────────
elif page == "❤️ Customer Health":
    st.title("❤️ Customer Health Scores")

    plan_filter = st.selectbox("Filter by Plan", 
                               ["All"] + list(health['plan'].unique()))
    
    filtered = health if plan_filter == "All" \
               else health[health['plan'] == plan_filter]
    filtered = filtered.copy()
    filtered['health_status_badge'] = filtered['health_status'].map({
        'Healthy': '🟢 Healthy',
        'At Risk': '🟡 At Risk',
        'Critical': '🔴 Critical'
    })

    col1, col2, col3 = st.columns(3)
    col1.metric("Healthy",  len(filtered[filtered.health_status=='Healthy']))
    col2.metric("At Risk",  len(filtered[filtered.health_status=='At Risk']))
    col3.metric("Critical", len(filtered[filtered.health_status=='Critical']))

    st.dataframe(
        filtered[['customer_id','plan','mrr','health_score','health_status_badge']]
        .sort_values('health_score'),
        width='stretch'
    )

# ── PAGE 3 ──────────────────────────────────────────
elif page == "🔍 Outlier Detection":
    st.title("🔍 Outlier Detection (IQR Method)")

    col1, col2 = st.columns(2)
    upsell   = outlier[outlier.outlier_flag.str.contains('Upsell')]
    downgrade = outlier[outlier.outlier_flag.str.contains('Downgrade')]
    col1.metric("Upsell Opportunities",  len(upsell))
    col2.metric("Downgrade Risks",       len(downgrade))

    st.subheader("All Outliers")
    st.dataframe(outlier, width='stretch')

    fig, ax = plt.subplots(figsize=(8,4))
    outlier.groupby('outlier_flag')['mrr'].count().plot(
        kind='bar', ax=ax, color=['tomato','steelblue']
    )
    ax.set_title("Outlier Count by Type")
    ax.set_ylabel("Count")
    st.pyplot(fig)

# ── PAGE 4 ──────────────────────────────────────────
elif page == "⚠️ Churn Prediction":
    st.title("⚠️ Churn Prediction")

    active = subs[subs.status == 'active'].copy()
    if 'churn_probability' in active.columns:
        threshold = st.slider("Churn Probability Threshold", 0.0, 1.0, 0.50, 0.05)
        st.caption("Active customers with churn probability above this threshold are considered at risk.")
        at_risk = active[active.churn_probability >= threshold]
        display_cols = ['customer_id', 'plan', 'mrr', 'churn_probability', 'health_score', 'health_status']
    else:
        threshold = st.slider("Health Score Threshold", 0, 100, 50, 5)
        st.caption("Customers with health score below this threshold are considered at risk.")
        at_risk = active[active.health_score < threshold]
        display_cols = ['customer_id', 'plan', 'mrr', 'health_score', 'health_status']

    col1, col2 = st.columns(2)
    col1.metric("At-Risk Customers", len(at_risk))
    col2.metric("Revenue at Risk", f"${at_risk['mrr'].sum():,.0f}/month")

    if at_risk_file is not None and not at_risk_file.empty:
        st.info(
            f"Loaded {len(at_risk_file)} precomputed at-risk accounts from data/at_risk_customers.csv. "
            "Use the slider to adjust the current risk threshold."
        )

    st.subheader("Top At-Risk Accounts")
    st.dataframe(
        at_risk[display_cols]
        .sort_values('mrr', ascending=False)
        .head(20),
        width='stretch'
    )