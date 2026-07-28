import sqlite3

conn = sqlite3.connect("data/inventory.db")
cursor = conn.cursor()

try:
    cursor.execute("""
        ALTER TABLE inventory
        ADD COLUMN reorder_threshold REAL DEFAULT 10
    """)
    conn.commit()
    print("✅ reorder_threshold column added successfully!")
except sqlite3.OperationalError as e:
    print(f"⚠️ {e}")

conn.close()