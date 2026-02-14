import sqlite3

def init_db():
    conn = sqlite3.connect('business_data.db')
    cursor = conn.cursor()
    
    # 1. Supplier ki Table
    cursor.execute('''CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY, name TEXT, risk_level TEXT)''')
    
    # 2. Invoices ki Table (Immediate Context)
    cursor.execute('''CREATE TABLE IF NOT EXISTS invoices (id TEXT PRIMARY KEY, supplier_id INTEGER, amount REAL, status TEXT)''')
    
    # 3. Kuch dummy suppliers daal dete hain testing ke liye
    suppliers = [
        (1, 'Supplier XYZ', 'Medium'),
        (2, 'TechCorp Inc', 'Low'),
        (3, 'Global Logistics', 'High')
    ]
    cursor.executemany('INSERT OR IGNORE INTO suppliers VALUES (?,?,?)', suppliers)
    
    conn.commit()
    conn.close()
    print("✅ Database initialized with dummy suppliers!")

if __name__ == "__main__":
    init_db()