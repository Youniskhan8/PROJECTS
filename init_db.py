import sqlite3

# Connect to (or create) users.db
conn = sqlite3.connect("users.db")

# Create users table
conn.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
''')

conn.commit()
conn.close()

print("✅ users.db created and users table initialized.")


