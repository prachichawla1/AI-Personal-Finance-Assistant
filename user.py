# user_data.py

user_profile = {
    "user_name": "Rohan Sharma",
    "current_balance": 45000.0,      # Current bank balance (INR)
    "minimum_balance_floor": 10000.0 # Emergency fund floor (cannot be touched)
}

# 60 days upcoming cashflow events
upcoming_events = [
    {"day": 5,  "type": "outflow", "name": "House Rent", "amount": 15000.0, "flexible": False},
    {"day": 10, "type": "outflow", "name": "Wifi & Utility Bills", "amount": 2500.0, "flexible": False},
    {"day": 12, "type": "outflow", "name": "Gym Subscription", "amount": 2000.0, "flexible": True},
    {"day": 30, "type": "inflow",  "name": "Salary Credit", "amount": 50000.0, "flexible": False},
    {"day": 35, "type": "outflow", "name": "House Rent", "amount": 15000.0, "flexible": False},
    {"day": 40, "type": "outflow", "name": "Grocery & Mess", "amount": 8000.0, "flexible": False},
]