import sqlite3
import pandas as pd
import numpy as np
import datetime
import random

DB_NAME = "finance_vault.db"

class AutonomousFinanceAgent:
    def __init__(self):
        self.db = DB_NAME

    def auto_sync_feed(self, feed_csv_path="sample_passbook.csv"):
        conn = sqlite3.connect(self.db)
        cur = conn.cursor()
        
        try:
            df_feed = pd.read_csv(feed_csv_path)
            for _, row in df_feed.iterrows():
                cur.execute("""
                    SELECT COUNT(*) FROM transactions 
                    WHERE date = ? AND description = ? AND amount = ?
                """, (str(row['date']), str(row['description']), float(row['amount'])))
                if cur.fetchone()[0] == 0:
                    cur.execute("""
                        INSERT INTO transactions (date, description, type, amount, category)
                        VALUES (?, ?, ?, ?, ?)
                    """, (str(row['date']), str(row['description']), str(row['type']).lower(), float(row['amount']), str(row['category'])))
        except Exception:
            pass

        simulated_expenses = [
            ("Swiggy Gourmet Dinner", "debit", 1450.0, "Food & Dining"),
            ("QuickMart Fresh Groceries", "debit", 2150.0, "Groceries"),
            ("Myntra Weekend Sale", "debit", 3800.0, "Shopping"),
            ("Uber City Ride", "debit", 650.0, "Utilities"),
            ("Starbucks Coffee Meet", "debit", 780.0, "Food & Dining"),
            ("Unplanned Electronics Purchase", "debit", 5400.0, "Shopping")
        ]
        
        new_item = random.choice(simulated_expenses)
        today_str = datetime.date.today().strftime("%Y-%m-%d")
        
        cur.execute("""
            INSERT INTO transactions (date, description, type, amount, category)
            VALUES (?, ?, ?, ?, ?)
        """, (today_str, new_item[0], new_item[1], new_item[2], new_item[3]))
        
        conn.commit()
        conn.close()
        return new_item

    def get_ledger(self):
        conn = sqlite3.connect(self.db)
        df = pd.read_sql_query("SELECT date, description, type, amount, category FROM transactions ORDER BY rowid DESC", conn)
        conn.close()
        return df

    def evaluate_financial_state(self):
        df = self.get_ledger()
        if df.empty:
            return None
        
        credits = df[df['type'] == 'credit']['amount'].sum()
        debits = df[df['type'] == 'debit']['amount'].sum()
        current_balance = credits - debits
        
        debit_df = df[df['type'] == 'debit'].copy()
        cat_spend = debit_df.groupby('category')['amount'].sum()
        
        salaries = df[df['description'].str.contains("Salary", case=False, na=False)]
        baseline_salary = float(salaries.iloc[0]['amount']) if not salaries.empty else 55000.0
        
        needs_cap = baseline_salary * 0.50
        wants_cap = baseline_salary * 0.30
        savings_cap = baseline_salary * 0.20
        
        essential_spend = cat_spend.get("Housing", 0) + cat_spend.get("Utilities", 0) + cat_spend.get("Groceries", 0)
        discretionary_spend = cat_spend.get("Shopping", 0) + cat_spend.get("Food & Dining", 0)
        
        mean_tx = debit_df['amount'].mean() if not debit_df.empty else 0
        std_tx = debit_df['amount'].std() if not debit_df.empty else 0
        threshold = mean_tx + (1.2 * std_tx)
        spikes = debit_df[debit_df['amount'] > threshold]
        
        days_remaining = max(5, 30 - min(25, len(debit_df)))
        rem_wants = wants_cap - discretionary_spend
        
        if rem_wants <= 0:
            daily_safe_runway = 0.0
        else:
            daily_safe_runway = rem_wants / days_remaining

        return {
            "inflow": credits,
            "outflow": debits,
            "balance": current_balance,
            "salary": baseline_salary,
            "needs_cap": needs_cap,
            "wants_cap": wants_cap,
            "savings_cap": savings_cap,
            "essential_spend": essential_spend,
            "discretionary_spend": discretionary_spend,
            "daily_runway": daily_safe_runway,
            "threshold": threshold,
            "spikes": spikes,
            "cat_spend": cat_spend,
            "days_remaining": days_remaining
        }

    def generate_autonomous_guidance(self, state):
        guidance = []
        if state['essential_spend'] <= state['needs_cap']:
            guidance.append(f"✅ **Fixed Overheads Stable:** INR {state['essential_spend']:,.0f} utilized out of INR {state['needs_cap']:,.0f} essential ceiling.")
        else:
            guidance.append(f"⚠️ **Needs Exceeded:** Essential commitments crossed 50% cap by INR {(state['essential_spend'] - state['needs_cap']):,.0f}.")

        if state['discretionary_spend'] > state['wants_cap']:
            guidance.append(f"🚨 **Discretionary Budget Breached:** You spent INR {state['discretionary_spend']:,.0f} against your INR {state['wants_cap']:,.0f} cap. Daily discretionary burn rate is restricted to INR 0.")
        else:
            guidance.append(f"🛡️ **Dynamic Daily Guard:** Remaining discretionary allowance: INR {(state['wants_cap'] - state['discretionary_spend']):,.0f}. Recommended burn rate: **INR {state['daily_runway']:,.0f} / day**.")

        if state['balance'] >= state['savings_cap']:
            guidance.append(f"🔒 **Emergency Reserve Protected:** Your reserve floor of INR {state['savings_cap']:,.0f} is completely secure. Net surplus: INR {state['balance']:,.0f}.")
        else:
            guidance.append(f"⚠️ **Emergency Cushion Alert:** Liquidity fell below INR {state['savings_cap']:,.0f}. Defer all discretionary retail orders.")
            
        return guidance