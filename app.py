import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

st.set_page_config(
    page_title="Subscription Health Monitor",
    layout="wide",
    page_icon="📊"
)

# ── Custom CSS for better looks ──────────────────────
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .metric-card {
        background: white;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        text-align: center;
    }
    .metric-value { font-size: 2rem; font-weight: 700; color: #1f2937; }
    .metric-label { font-size: 0.9rem; color: #6b7280; margin-top: 4px; }
    .section-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #374151;
        margin: 20px 0 10px 0;
        padding-bottom: 6px;
        border-bottom: 2px solid #e5e7eb;
    }
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 16px 20px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.07);
    }
    .stSelectbox > div { border-radius: 8px; }
    h1 { color: #111827 !important; }
</style>
""", unsafe_allow_html=True)

# ── Load Data ────────────────────────────────────────
@st.cache_data
def load_data():
    subs    = pd.read_csv('data/subscriptions_scored.csv')
    mrr     = pd.read_csv('data/mrr_monthly.csv')
    health  = pd.read_csv('data/health_scores.csv')
    outlier = pd.read_csv('data/outliers.csv')
    return subs, mrr, health, outlier

subs, mrr, health, outlier = load_data()

# Merge health score into subs so churn page has all columns
if 'health_score' not in subs.columns:
    subs = subs.merge(
        health[['customer_id','health_score','health_status']],
        on='customer_id', how='left'
    )

# ── Sidebar ───────────────────────────────────────────
st.sidebar.image("https://img.icons8.com/fluency/96/combo-chart.png", width=60)
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", [
    "📈 MRR Overview",
    "❤️ Customer Health",
    "🔍 Outlier Detection",
    "⚠️ Churn Prediction"
])

st.sidebar.markdown("---")
st.sidebar.markdown("**Dataset**")
st.sidebar.markdown(f"🧑‍💼 {len(subs):,} total customers")
st.sidebar.markdown(f"✅ {len(subs[subs.status=='active']):,} active")
st.sidebar.markdown(f"❌ {len(subs[subs.status=='churned']):,} churned")

# ════════════════════════════════════════════════════
# PAGE 1 — MRR OVERVIEW
# ════════════════════════════════════════════════════
if page == "📈 MRR Overview":
    st.title("📈 MRR Overview")
    st.markdown("Monthly Recurring Revenue trends and growth analysis.")
    st.markdown("---")

    active = subs[subs.status == 'active']
    total_mrr = active['mrr'].sum()
    churned_mrr = subs[subs.status == 'churned']['mrr'].sum()
    avg_mrr = active['mrr'].mean()

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("💰 Total MRR",        f"${total_mrr:,.0f}")
    col2.metric("👥 Active Customers",  f"{len(active):,}")
    col3.metric("📉 Churned MRR",       f"${churned_mrr:,.0f}")
    col4.metric("📊 Avg MRR/Customer",  f"${avg_mrr:,.0f}")

    st.markdown("---")

    # MRR Line Chart
    st.markdown('<p class="section-title">Monthly MRR Growth</p>', unsafe_allow_html=True)
    fig, ax = plt.subplots(figsize=(11, 4))
    fig.patch.set_facecolor('white')
    ax.set_facecolor('#f8f9fa')
    ax.plot(mrr['month'], mrr['total_mrr'], marker='o',
            color='#3b82f6', linewidth=2.5, markersize=6)
    ax.fill_between(range(len(mrr)), mrr['total_mrr'],
                    alpha=0.1, color='#3b82f6')
    ax.set_xticks(range(len(mrr)))
    ax.set_xticklabels(mrr['month'], rotation=45, ha='right', fontsize=9)
    ax.set_ylabel("MRR ($)", fontsize=10)
    ax.set_title("Total MRR by Month", fontsize=12, fontweight='bold')
    ax.grid(axis='y', linestyle='--', alpha=0.5)
    ax.spines[['top','right']].set_visible(False)
    plt.tight_layout()
    st.pyplot(fig)

    # MRR by Plan
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">MRR by Plan</p>', unsafe_allow_html=True)
        plan_mrr = active.groupby('plan')['mrr'].sum().sort_values(ascending=True)
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        colors = ['#93c5fd','#60a5fa','#3b82f6','#1d4ed8']
        ax2.barh(plan_mrr.index, plan_mrr.values, color=colors)
        ax2.set_xlabel("MRR ($)")
        ax2.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig2)

    with col2:
        st.markdown('<p class="section-title">Customers by Plan</p>', unsafe_allow_html=True)
        plan_count = active.groupby('plan').size()
        fig3, ax3 = plt.subplots(figsize=(5, 3))
        ax3.pie(plan_count.values, labels=plan_count.index,
                autopct='%1.0f%%', colors=['#bfdbfe','#93c5fd','#60a5fa','#3b82f6'])
        plt.tight_layout()
        st.pyplot(fig3)

    st.markdown('<p class="section-title">Full MRR Table</p>', unsafe_allow_html=True)
    st.dataframe(mrr, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════
# PAGE 2 — CUSTOMER HEALTH
# ════════════════════════════════════════════════════
elif page == "❤️ Customer Health":
    st.title("❤️ Customer Health Scores")
    st.markdown("Every active customer scored 0–100 based on tenure, usage, features and support signals.")
    st.markdown("---")

    col1, col2 = st.columns(2)
    plan_filter = col1.selectbox("Filter by Plan", ["All"] + sorted(health['plan'].unique().tolist()))
    status_filter = col2.selectbox("Filter by Health Status", ["All", "Healthy", "At Risk", "Critical"])

    filtered = health.copy()
    if plan_filter != "All":
        filtered = filtered[filtered['plan'] == plan_filter]
    if status_filter != "All":
        filtered = filtered[filtered['health_status'] == status_filter]

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("🟢 Healthy",  len(filtered[filtered.health_status == 'Healthy']))
    col2.metric("🟡 At Risk",  len(filtered[filtered.health_status == 'At Risk']))
    col3.metric("🔴 Critical", len(filtered[filtered.health_status == 'Critical']))

    # Health distribution chart
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Health Status Distribution</p>', unsafe_allow_html=True)
        status_counts = health['health_status'].value_counts()
        colors_map = {'Healthy': '#22c55e', 'At Risk': '#f59e0b', 'Critical': '#ef4444'}
        colors_list = [colors_map.get(s, '#gray') for s in status_counts.index]
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.bar(status_counts.index, status_counts.values, color=colors_list, edgecolor='white')
        ax.set_ylabel("Customers")
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.markdown('<p class="section-title">Health Score Distribution</p>', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        ax2.hist(health['health_score'], bins=20, color='#3b82f6',
                 edgecolor='white', alpha=0.8)
        ax2.axvline(75, color='#22c55e', linestyle='--', label='Healthy (75)')
        ax2.axvline(50, color='#f59e0b', linestyle='--', label='At Risk (50)')
        ax2.set_xlabel("Health Score")
        ax2.set_ylabel("Count")
        ax2.legend(fontsize=8)
        ax2.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig2)

    st.markdown('<p class="section-title">Customer Table</p>', unsafe_allow_html=True)

    def highlight_status(val):
        colors = {
            'Healthy':  'background-color:#dcfce7; color:#166534',
            'At Risk':  'background-color:#fef9c3; color:#854d0e',
            'Critical': 'background-color:#fee2e2; color:#991b1b'
        }
        return colors.get(val, '')

    display = filtered[['customer_id','plan','mrr','health_score','health_status']].sort_values('health_score')
    st.dataframe(
        display.style.applymap(highlight_status, subset=['health_status']),
        use_container_width=True,
        hide_index=True
    )

# ════════════════════════════════════════════════════
# PAGE 3 — OUTLIER DETECTION
# ════════════════════════════════════════════════════
elif page == "🔍 Outlier Detection":
    st.title("🔍 Outlier Detection")
    st.markdown("IQR-based revenue outlier detection — identifying upsell opportunities and downgrade risks.")
    st.markdown("---")

    upsell   = outlier[outlier.outlier_flag.str.contains('Upsell',   na=False)]
    downgrade = outlier[outlier.outlier_flag.str.contains('Downgrade', na=False)]

    col1, col2, col3 = st.columns(3)
    col1.metric("🔼 Upsell Opportunities",  len(upsell))
    col2.metric("🔽 Downgrade Risks",        len(downgrade))
    col3.metric("📊 Total Outliers",         len(outlier))

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Outliers by Type</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(5, 3))
        counts = outlier['outlier_flag'].value_counts()
        ax.bar(counts.index, counts.values,
               color=['#3b82f6','#ef4444'], edgecolor='white')
        ax.set_ylabel("Count")
        ax.tick_params(axis='x', labelsize=8)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.markdown('<p class="section-title">Outlier MRR by Plan</p>', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        plan_outlier = outlier.groupby('plan')['mrr'].sum().sort_values()
        ax2.barh(plan_outlier.index, plan_outlier.values, color='#8b5cf6')
        ax2.set_xlabel("Total MRR ($)")
        ax2.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig2)

    st.markdown('<p class="section-title">All Outlier Accounts</p>', unsafe_allow_html=True)
    st.dataframe(outlier, use_container_width=True, hide_index=True)

# ════════════════════════════════════════════════════
# PAGE 4 — CHURN PREDICTION
# ════════════════════════════════════════════════════
elif page == "⚠️ Churn Prediction":
    st.title("⚠️ Churn Prediction")
    st.markdown("Machine learning model predicting which active customers are likely to churn.")
    st.markdown("---")

    active = subs[subs.status == 'active'].copy()

    threshold = st.slider("🎚️ Risk Threshold", 0.0, 1.0, 0.50, 0.05,
                          help="Move left to be more aggressive, right to be more conservative")
    st.caption(f"Showing customers with churn probability above **{threshold}**")

    at_risk = active[active['churn_probability'] >= threshold].sort_values('mrr', ascending=False)

    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    col1.metric("⚠️ At-Risk Customers",  f"{len(at_risk):,}")
    col2.metric("💸 Revenue at Risk",     f"${at_risk['mrr'].sum():,.0f}/month")
    col3.metric("📊 Avg Churn Prob",      f"{at_risk['churn_probability'].mean():.0%}" if len(at_risk) > 0 else "0%")

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<p class="section-title">Churn Probability Distribution</p>', unsafe_allow_html=True)
        fig, ax = plt.subplots(figsize=(5, 3))
        ax.hist(active['churn_probability'], bins=25,
                color='#3b82f6', edgecolor='white', alpha=0.8)
        ax.axvline(threshold, color='#ef4444', linestyle='--',
                   linewidth=2, label=f'Threshold: {threshold}')
        ax.set_xlabel("Churn Probability")
        ax.set_ylabel("Customers")
        ax.legend(fontsize=8)
        ax.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig)

    with col2:
        st.markdown('<p class="section-title">At-Risk Revenue by Plan</p>', unsafe_allow_html=True)
        fig2, ax2 = plt.subplots(figsize=(5, 3))
        if len(at_risk) > 0:
            risk_plan = at_risk.groupby('plan')['mrr'].sum().sort_values()
            ax2.barh(risk_plan.index, risk_plan.values, color='#ef4444', alpha=0.8)
            ax2.set_xlabel("Revenue at Risk ($)")
            ax2.spines[['top','right']].set_visible(False)
        plt.tight_layout()
        st.pyplot(fig2)

    st.markdown('<p class="section-title">Top At-Risk Accounts</p>', unsafe_allow_html=True)
    if len(at_risk) > 0:
        display_cols = ['customer_id', 'plan', 'mrr', 'churn_probability']
        if 'health_score' in at_risk.columns:
            display_cols += ['health_score', 'health_status']
        st.dataframe(
            at_risk[display_cols].head(20),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.info("No customers above this threshold. Try lowering the slider.")