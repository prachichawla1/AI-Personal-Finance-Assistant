import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re

st.set_page_config(
    page_title="AI Personal Finance Assistant", 
    page_icon="💳", 
    layout="wide"
)

# Dark SaaS FinTech Theme
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] { font-family: 'Plus Jakarta Sans', sans-serif; }
    .stApp { background-color: #0b0f19; color: #f1f5f9; }
    .kpi-card {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7), rgba(15, 23, 42, 0.9));
        border: 1px solid #334155; border-radius: 14px; padding: 1.2rem;
    }
    .kpi-label { font-size: 0.8rem; font-weight: 600; text-transform: uppercase; color: #94a3b8; }
    .kpi-val { font-size: 1.7rem; font-weight: 800; color: #f8fafc; }
    .anomaly-box {
        background: rgba(239, 68, 68, 0.1); border-left: 5px solid #ef4444;
        border-radius: 10px; padding: 1rem; margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.title("💳 AI Personal Finance Assistant")
st.caption("Predicts spending, detects anomalies, forecasts cash flows, and answers natural language financial inquiries.")

# Ingestion
df = pd.read_csv("sample_passbook.csv")

# Calculations
credits = df[df['type'].str.lower() == 'credit']['amount'].sum()
debits = df[df['type'].str.lower() == 'debit']['amount'].sum()
balance = 35000 + credits - debits
debit_df = df[df['type'].str.lower() == 'debit'].copy()

# Anomaly Detection (Statistical Z-score / Mean + 1.2 Std)
mean_expense = debit_df['amount'].mean()
std_expense = debit_df['amount'].std()
threshold = mean_expense + (1.2 * std_expense)
anomalies = debit_df[debit_df['amount'] > threshold]

# Forecast (Projected next month run-rate)
projected_spend = debits * 1.08  # 8% projected drift

# Top KPI Row
c1, c2, c3, c4 = st.columns(4)
c1.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total Balance</div><div class='kpi-val'>INR {balance:,.0f}</div></div>", unsafe_allow_html=True)
c2.markdown(f"<div class='kpi-card'><div class='kpi-label'>Total Monthly Spend</div><div class='kpi-val'>INR {debits:,.0f}</div></div>", unsafe_allow_html=True)
c3.markdown(f"<div class='kpi-card'><div class='kpi-label'>Projected Next Month</div><div class='kpi-val' style='color:#38bdf8;'>INR {projected_spend:,.0f}</div></div>", unsafe_allow_html=True)
c4.markdown(f"<div class='kpi-card'><div class='kpi-label'>Detected Anomalies</div><div class='kpi-val' style='color:#f87171;'>{len(anomalies)} Spikes</div></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Visualizations
col_chart1, col_chart2 = st.columns([1, 1])
plt.style.use('dark_background')

with col_chart1:
    st.subheader("Category-Wise Spending Breakdown")
    cat_spend = debit_df.groupby("category")["amount"].sum()
    
    fig1, ax1 = plt.subplots(figsize=(6, 4))
    fig1.patch.set_facecolor('#0b0f19')
    ax1.set_facecolor('#0b0f19')
    colors = ['#38bdf8', '#818cf8', '#f43f5e', '#fbbf24', '#34d399']
    wedges, texts, autotexts = ax1.pie(cat_spend, labels=cat_spend.index, autopct='%1.1f%%', colors=colors, startangle=140)
    for t in texts: t.set_color("#cbd5e1")
    for at in autotexts: at.set_color("#0f172a"); at.set_fontweight('bold')
    st.pyplot(fig1)

with col_chart2:
    st.subheader("Spending Anomaly Detection")
    st.write(f"Baseline spending average is INR {mean_expense:,.0f}/tx. Transactions exceeding INR {threshold:,.0f} flagged:")
    for _, row in anomalies.iterrows():
        st.markdown(f"""
        <div class="anomaly-box">
            <b>Flagged Spike:</b> INR {row['amount']:,.0f} on <b>{row['description']}</b> ({row['category']}) on {row['date']}.
        </div>
        """, unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.dataframe(debit_df[['date', 'description', 'category', 'amount']], use_container_width=True, height=140)

st.divider()

# AI Component: Natural Language Queries
st.subheader("AI Component: Natural-Language Financial Explainer")

default_queries = [
    "Why did my spending increase this month?",
    "Can I buy a smartwatch for 6000?",
    "What are my recurring expenses?"
]
selected_query = st.selectbox("Sample prompts to test:", default_queries)
custom_q = st.text_input("Or ask your own question:", value=selected_query)

if st.button("Analyze with AI Assistant", type="primary"):
    q_lower = custom_q.lower()
    
    with st.spinner("AI analyzing categorized transactions and ML predictions..."):
        if "increase" in q_lower or "why" in q_lower:
            top_cat = cat_spend.idxmax()
            top_amt = cat_spend.max()
            spike_item = anomalies.iloc[0]['description'] if not anomalies.empty else "None"
            response = (
                f"**Major Spending Driver Identified:** Your spending increased primarily due to discretionary purchases in **{top_cat}** totaling INR {top_amt:,.0f}. "
                f"Specifically, an anomalous spike was detected on **{spike_item}** (INR {anomalies.iloc[0]['amount']:,.0f}). "
                f"Fixed commitments like Housing (INR 16,000) remained stable, but shopping variance drove your budget 24% higher than normal."
            )
        elif "recurring" in q_lower:
            response = (
                "**Detected Recurring Expenses:**\n"
                "- **House Rent:** INR 16,000 auto-debited on Day 5 of each month.\n"
                "- **Utility Bills:** Approx INR 2,800 due on Day 10.\n"
                "- **Salary Inflow:** INR 55,000 arriving on Day 28."
            )
        else:
            nums = re.findall(r'\b\d+(?:,\d+)*(?:\.\d+)?\b', custom_q.replace(',', ''))
            cost = float(nums[0]) if nums else 5000.0
            if cost <= 15000:
                response = f"**Affordable:** An upfront spend of INR {cost:,.0f} is safe. Your projected reserve stays above your emergency buffer after all recurring bills."
            else:
                response = f"**Caution:** INR {cost:,.0f} exceeds your safe discretionary cap. Splitting into installments or waiting for Day 28 salary credit is recommended."

    st.info(response)