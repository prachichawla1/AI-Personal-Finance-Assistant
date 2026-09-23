import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from database import init_db, reset_db_to_positive
from agent_core import AutonomousFinanceAgent

st.set_page_config(
    page_title="FinGuardian AI", 
    page_icon="🛡️", 
    layout="wide"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
    .stApp { background-color: #0b0f19; color: #e2e8f0; }
    .agent-header {
        background: linear-gradient(135deg, #1e293b, #0f172a);
        border: 1px solid #334155; border-radius: 12px; padding: 1.5rem; margin-bottom: 1.2rem;
    }
    .kpi-block {
        background: #1e293b; border: 1px solid #334155; border-radius: 10px; padding: 1rem;
    }
    .advisor-bullet {
        background: rgba(56, 189, 248, 0.08); border-left: 4px solid #38bdf8;
        border-radius: 8px; padding: 0.9rem; margin: 0.6rem 0; font-size: 0.95rem;
    }
    .spike-bullet {
        background: rgba(239, 68, 68, 0.08); border-left: 4px solid #ef4444;
        border-radius: 8px; padding: 0.8rem; margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

init_db()
agent = AutonomousFinanceAgent()

# ----------------- SIDEBAR -----------------
st.sidebar.markdown("### 🔄 FinGuardian Operations")
st.sidebar.caption("Simulate live banking feeds or reset to fresh baseline.")

if st.sidebar.button("Fetch & Sync Live Debit", type="primary", use_container_width=True):
    new_tx = agent.auto_sync_feed("sample_passbook.csv")
    st.toast(f"New Bank Debit Ingested: {new_tx[0]} (INR {new_tx[2]:,.0f})", icon="💳")
    st.rerun()

if st.sidebar.button("🧹 Reset to Healthy Month (Positive)", use_container_width=True):
    reset_db_to_positive()
    st.sidebar.success("Database restored to healthy positive balance!")
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("#### Capital Rules:")
st.sidebar.markdown("""
- **50% Needs:** Housing, Utilities & Groceries
- **30% Discretionary:** Lifestyle & Dining
- **20% Reserve:** Emergency Vault
- **Dynamic Guard:** Safe Daily Allowance
""")

state = agent.evaluate_financial_state()

if state is None:
    reset_db_to_positive()
    st.rerun()

# Header
st.markdown("""
<div class="agent-header">
    <h2 style="margin:0; color:#38bdf8;">🛡️ FinGuardian AI: Personal Wealth Advisor</h2>
    <p style="margin-top:0.4rem; color:#94a3b8;">
        Real-time financial intelligence: 50/30/20 capital allocation, dynamic daily spending limits, statistical anomaly detection, and automated audits.
    </p>
</div>
""", unsafe_allow_html=True)

# Metrics
k1, k2, k3, k4 = st.columns(4)
k1.markdown(f"<div class='kpi-block'><span style='color:#94a3b8; font-size:0.75rem;'>VERIFIED MONTHLY SALARY</span><h3 style='margin:0.2rem 0; color:#38bdf8;'>INR {state['salary']:,.0f}</h3></div>", unsafe_allow_html=True)
k2.markdown(f"<div class='kpi-block'><span style='color:#94a3b8; font-size:0.75rem;'>SAFE DAILY ALLOWANCE</span><h3 style='margin:0.2rem 0; color:#fbbf24;'>INR {state['daily_runway']:,.0f} / day</h3></div>", unsafe_allow_html=True)
k3.markdown(f"<div class='kpi-block'><span style='color:#94a3b8; font-size:0.75rem;'>TOTAL OUTFLOW TO DATE</span><h3 style='margin:0.2rem 0; color:#f87171;'>INR {state['outflow']:,.0f}</h3></div>", unsafe_allow_html=True)
k4.markdown(f"<div class='kpi-block'><span style='color:#94a3b8; font-size:0.75rem;'>NET REMAINING LIQUIDITY</span><h3 style='margin:0.2rem 0; color:#34d399;'>INR {state['balance']:,.0f}</h3></div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Guidance
st.subheader("🧭 Real-Time Advisory & Spending Directives")
guidance_points = agent.generate_autonomous_guidance(state)
for point in guidance_points:
    st.markdown(f"<div class='advisor-bullet'>{point}</div>", unsafe_allow_html=True)

tab_alloc, tab_spikes, tab_vault = st.tabs([
    "📊 Capital Allocation & Compliance", 
    "🚨 Flagged Outlier Spikes", 
    "📂 Secure SQLite Vault"
])

with tab_alloc:
    c_left, c_right = st.columns(2)
    with c_left:
        st.write("<b>Category Spending Breakdown:</b>", unsafe_allow_html=True)
        plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(5, 3.5))
        fig.patch.set_facecolor('#0b0f19')
        ax.set_facecolor('#0b0f19')
        colors = ['#38bdf8', '#818cf8', '#f43f5e', '#fbbf24', '#34d399', '#f97316', '#a78bfa']
        wedges, texts, autotexts = ax.pie(state['cat_spend'], labels=state['cat_spend'].index, autopct='%1.1f%%', colors=colors[:len(state['cat_spend'])], startangle=140)
        for t in texts: t.set_color("#94a3b8")
        for at in autotexts: at.set_color("#0f172a"); at.set_fontweight('bold')
        st.pyplot(fig)
        
    with c_right:
        st.write("<b>50/30/20 Budget Compliance:</b>", unsafe_allow_html=True)
        comp_df = pd.DataFrame({
            "Pillar": ["Needs (50%)", "Wants (30%)", "Savings Floor (20%)"],
            "Target Cap (INR)": [state['needs_cap'], state['wants_cap'], state['savings_cap']],
            "Actual Realized (INR)": [state['essential_spend'], state['discretionary_spend'], state['balance']]
        })
        st.dataframe(comp_df, use_container_width=True)

with tab_spikes:
    st.subheader("Statistical Outlier Detection")
    st.caption(f"Expenses exceeding dynamic boundary of INR {state['threshold']:,.0f} (Mean + 1.2 * StdDev):")
    if not state['spikes'].empty:
        for _, row in state['spikes'].iterrows():
            st.markdown(f"""
            <div class='spike-bullet'>
                <b>⚠️ Flagged Outlier:</b> INR {row['amount']:,.0f} debited for <b>{row['description']}</b> ({row['category']}) on {row['date']}.
            </div>
            """, unsafe_allow_html=True)
    else:
        st.success("All transactions are within normal statistical spending boundaries.")

with tab_vault:
    st.subheader("FinGuardian Vault Ledger (inance_vault.db)")
    st.caption("Transactions stored persistently in SQLite. Top record is the latest transaction:")
    st.dataframe(agent.get_ledger(), use_container_width=True)

st.divider()

# Explainer
st.subheader("💬 Consult FinGuardian AI")
user_query = st.text_input("Ask a question regarding your financial state:", value="Why did my spending increase this month?")
if st.button("Generate Diagnostic Output", type="primary"):
    q_norm = user_query.lower()
    if "increase" in q_norm or "why" in q_norm:
        st.info(f"**FinGuardian Diagnostic:** Fixed commitments remained stable. Spending inflation was driven by discretionary purchases in **{state['cat_spend'].idxmax()}**, including an anomalous spike on {state['spikes'].iloc[0]['description'] if not state['spikes'].empty else 'shopping'} (INR {state['spikes'].iloc[0]['amount']:,.0f}).")
    elif "daily" in q_norm or "allowance" in q_norm:
        st.info(f"**FinGuardian Diagnostic:** To preserve your 20% savings floor, your safe discretionary burn rate is **INR {state['daily_runway']:,.0f} per day** for the remaining cycle.")
    else:
        st.info(f"**FinGuardian Diagnostic:** Available liquidity is INR {state['balance']:,.0f}, maintaining complete protection of your emergency reserve floor (INR {state['savings_cap']:,.0f}).")