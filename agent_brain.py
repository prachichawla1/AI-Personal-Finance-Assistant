import pandas as pd
import json

def analyze_raw_financial_data(csv_file_or_df):
    if isinstance(csv_file_or_df, str):
        df = pd.read_csv(csv_file_or_df)
    else:
        df = csv_file_or_df
        
    df.columns = [c.strip().lower() for c in df.columns]
    
    credits = df[df['type'].str.lower() == 'credit']['amount'].sum()
    debits = df[df['type'].str.lower() == 'debit']['amount'].sum()
    
    salary_rows = df[(df['type'].str.lower() == 'credit') & (df['description'].str.contains('salary|stipend|payroll', case=False, na=False))]
    detected_salary = float(salary_rows['amount'].iloc[-1]) if not salary_rows.empty else 55000.0
    
    rent_rows = df[df['description'].str.contains('rent|house', case=False, na=False)]
    detected_rent = float(rent_rows['amount'].iloc[-1]) if not rent_rows.empty else 16000.0
    
    starting_balance = 35000.0
    current_balance = float(starting_balance + credits - debits)
    emergency_floor = max(10000.0, detected_rent * 0.8)

    return {
        "current_balance": current_balance,
        "salary": detected_salary,
        "rent": detected_rent,
        "emergency_floor": emergency_floor
    }

def run_forward_projection(financial_state, requested_cost, days=60):
    bal = financial_state["current_balance"]
    floor = financial_state["emergency_floor"]
    rent = financial_state["rent"]
    salary = financial_state["salary"]
    
    trajectory_baseline = []
    trajectory_with_purchase = []
    
    for day in range(1, days + 1):
        if day == 5: bal -= rent
        if day == 12: bal -= 3000.0
        if day == 28 or day == 58: bal += salary
            
        trajectory_baseline.append(bal)
        trajectory_with_purchase.append(bal - requested_cost)
        
    lowest_after_purchase = min(trajectory_with_purchase)
    safe_spending_cap = max(0.0, min(trajectory_baseline) - floor)
    
    if lowest_after_purchase >= floor:
        verdict = "BUY_NOW"
    elif lowest_after_purchase >= 0:
        verdict = "BUY_WITH_RISK"
    else:
        verdict = "WAIT"
        
    return {
        "verdict": verdict,
        "safe_spending_cap": safe_spending_cap,
        "lowest_projected": lowest_after_purchase,
        "baseline": trajectory_baseline,
        "with_purchase": trajectory_with_purchase
    }

def ask_llm_agent(api_key, user_query, profile, simulation_result, target_cost):
    """
    Hybrid Agentic Advisor:
    Tries Google Gemini if a valid AIzaSy key is given; otherwise uses
    Deterministic Financial Persona Reasoning Engine.
    """
    # 1. If valid Gemini AIzaSy key is provided
    if api_key and api_key.startswith("AIzaSy"):
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel('gemini-1.5-flash')
            prompt = f"User asks: '{user_query}'. Target cost: INR {target_cost}. Current balance: INR {profile['current_balance']}. Emergency floor: INR {profile['emergency_floor']}. Simulation verdict: {simulation_result['verdict']}. Provide a 3-sentence professional financial advice."
            return model.generate_content(prompt).text
        except Exception:
            pass

    # 2. Local Intelligent Financial Advisor Engine (Deterministic Expert System)
    verdict = simulation_result['verdict']
    floor = profile['emergency_floor']
    lowest = simulation_result['lowest_projected']
    safe_cap = simulation_result['safe_spending_cap']
    
    if verdict == "BUY_NOW":
        return (
            f"Based on forward simulation of your 60-day cash flow, this purchase of ₹{target_cost:,.0f} is fully safe. "
            f"Even after this transaction and your upcoming rent deduction (₹{profile['rent']:,.0f}), your lowest liquid reserve will remain at ₹{lowest:,.0f}, "
            f"which stays safely above your ₹{floor:,.0f} emergency threshold."
        )
    elif verdict == "BUY_WITH_RISK":
        emi = round(target_cost / 3, 0)
        return (
            f"Caution advised: Purchasing upfront will drop your cash balance to ₹{lowest:,.0f}, dangerously breaching your ₹{floor:,.0f} emergency reserve. "
            f"While you will not face an immediate overdraft, you will be financially vulnerable before your Day 28 salary. "
            f"Recommendation: Convert this into a 3-month EMI (approx ₹{emi:,.0f}/mo) or wait for salary credit."
        )
    else:
        deficit = abs(lowest)
        return (
            f"Critical financial hazard: You cannot afford ₹{target_cost:,.0f} upfront right now. "
            f"Your simulation reveals a projected deficit of ₹{deficit:,.0f} by Day 12 after scheduled rent and living obligations. "
            f"You must postpone this expenditure until your next salary settlement (+₹{profile['salary']:,.0f}) arrives on Day 28."
        )
