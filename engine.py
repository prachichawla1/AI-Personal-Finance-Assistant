from user_data import user_profile, upcoming_events

def simulate_cash_flow(total_days=60, exclude_event_names=None):
    if exclude_event_names is None:
        exclude_event_names = []
        
    balance = user_profile["current_balance"]
    timeline = []
    
    events_by_day = {}
    for ev in upcoming_events:
        if ev["name"] not in exclude_event_names:
            events_by_day.setdefault(ev["day"], []).append(ev)

    for day in range(1, total_days + 1):
        if day in events_by_day:
            for ev in events_by_day[day]:
                if ev["type"] == "inflow":
                    balance += ev["amount"]
                elif ev["type"] == "outflow":
                    balance -= ev["amount"]
        
        timeline.append({"day": day, "balance": balance})
        
    return timeline

def check_affordability(item_cost, timeline):
    min_floor = user_profile["minimum_balance_floor"]
    lowest_projected_balance = min(day_stat["balance"] for day_stat in timeline)
    
    safe_to_spend = max(0.0, lowest_projected_balance - min_floor)
    
    if item_cost <= safe_to_spend:
        status = "Affordable Now"
        recommendation = "Full upfront payment is completely safe. Liquid buffer remains untouched."
        plan = "Upfront Full Payment"
    elif lowest_projected_balance - item_cost >= 0:
        status = "Affordable With Risk"
        recommendation = "Violates your emergency buffer. You can pause flexible subscriptions (like Gym) or opt for installments."
        plan = "Consider 3-Month EMI or Pause Flexible Subscriptions"
    else:
        emi_cost = item_cost / 3
        if emi_cost <= safe_to_spend:
            status = "Affordable via Installments"
            recommendation = f"Upfront is risky, but a 3-month EMI of INR {emi_cost:,.2f}/mo safely protects your minimum floor."
            plan = f"3 Months EMI @ INR {emi_cost:,.2f}/mo"
        else:
            status = "Not Affordable"
            recommendation = "Severe cash deficit detected before the upcoming salary cycle. Postpone purchase until Day 30."
            plan = "Wait until Salary Settlement"
        
    return {
        "status": status,
        "recommendation": recommendation,
        "plan": plan,
        "lowest_balance": lowest_projected_balance,
        "safe_to_spend_limit": safe_to_spend
    }
