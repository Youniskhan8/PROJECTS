import sqlite3

def init_sales_db():
    with sqlite3.connect('sales.db') as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                product TEXT NOT NULL,
                quantity INTEGER NOT NULL,
                price REAL NOT NULL,
                date TEXT NOT NULL
            )
        ''')
        print("✅ sales.db and sales table created successfully!")

if __name__ == "__main__":
    init_sales_db()
