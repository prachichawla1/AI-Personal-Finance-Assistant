import sqlite3
import pandas as pd

DB_NAME = "finance_vault.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS transactions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            description TEXT,
            type TEXT,
            amount REAL,
            category TEXT
        )
    ''')
    conn.commit()
    conn.close()

def reset_db_to_positive():
    """Wipes corrupted negative debits and seeds a healthy positive month."""
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS transactions")
    conn.commit()
    conn.close()
    
    init_db()
    seed_default_data()

def add_transaction(t_date, description, t_type, amount, category):
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO transactions (date, description, type, amount, category)
        VALUES (?, ?, ?, ?, ?)
    ''', (t_date, description, t_type, amount, category))
    conn.commit()
    conn.close()

def get_all_transactions():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT date, description, type, amount, category FROM transactions ORDER BY rowid DESC", conn)
    conn.close()
    return df

def seed_default_data():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM transactions")
    count = cur.fetchone()[0]
    
    if count == 0:
        default_records = [
            ('2026-09-01', 'Opening Liquid Reserves', 'credit', 35000.0, 'Salary/Income'),
            ('2026-09-01', 'Monthly Salary Credited', 'credit', 55000.0, 'Salary/Income'),
            ('2026-09-03', 'Supermart Grocery', 'debit', 3200.0, 'Groceries'),
            ('2026-09-05', 'House Rent Auto-Debit', 'debit', 16000.0, 'Housing'),
            ('2026-09-08', 'Swiggy Delivery', 'debit', 850.0, 'Food & Dining'),
            ('2026-09-10', 'Electricity & Water Bill', 'debit', 2800.0, 'Utilities'),
            ('2026-09-14', 'Zara Retail Outflow', 'debit', 6500.0, 'Shopping'),
            ('2026-09-18', 'Local Mart Provisions', 'debit', 1900.0, 'Groceries'),
            ('2026-09-21', 'Cafe & Social Dining', 'debit', 950.0, 'Food & Dining')
        ]
        cur.executemany('''
            INSERT INTO transactions (date, description, type, amount, category)
            VALUES (?, ?, ?, ?, ?)
        ''', default_records)
        conn.commit()
    conn.close()