import re

def extract_financial_info_from_text(raw_text):
    """
    Bank SMS, Salary slips ya notes me se automatically balance, salary,
    rent aur target item amount extract karta hai.
    """
    extracted = {}
    lines = raw_text.splitlines()
    
    # 1. Salary Detection
    salary_match = re.search(r'(?:salary|credited|credited with|stipend)[^\d]*([\d,]+(?:\.\d+)?)', raw_text, re.IGNORECASE)
    if salary_match:
        extracted['salary'] = float(salary_match.group(1).replace(',', ''))
        
    # 2. Balance Detection
    bal_match = re.search(r'(?:balance|bal|avl bal|available)[^\d]*([\d,]+(?:\.\d+)?)', raw_text, re.IGNORECASE)
    if bal_match:
        extracted['balance'] = float(bal_match.group(1).replace(',', ''))
        
    # 3. Rent / Outflow Detection
    rent_match = re.search(r'(?:rent|house rent|debited for rent)[^\d]*([\d,]+(?:\.\d+)?)', raw_text, re.IGNORECASE)
    if rent_match:
        extracted['rent'] = float(rent_match.group(1).replace(',', ''))

    # 4. Item Price Detection (e.g. 'iPhone 45000' or 'Price: 25,000')
    price_match = re.search(r'(?:price|cost|worth|buy|purchase|rs\.?|inr)[^\d]*([\d,]+(?:\.\d+)?)', raw_text, re.IGNORECASE)
    if price_match:
        extracted['target_price'] = float(price_match.group(1).replace(',', ''))
        
    return extracted

def parse_receipt_image(uploaded_file):
    """
    Mock OCR parser: Image metadata ya typical receipt patterns se 
    total amount detect karta hai.
    """
    filename = uploaded_file.name.lower()
    
    # Demonstration smart fallback based on common invoices
    if "laptop" in filename or "macbook" in filename:
        return {"merchant": "Apple Store / Electronics", "amount": 65000.0}
    elif "phone" in filename or "iphone" in filename:
        return {"merchant": "Croma / Amazon", "amount": 42000.0}
    elif "bill" in filename or "rent" in filename:
        return {"merchant": "Utility / Landlord", "amount": 16500.0}
    else:
        # Default parsed receipt amount
        return {"merchant": "Detected Retail Invoice", "amount": 28500.0}
