import sqlite3

conn = sqlite3.connect("data/inventory.db")
cursor = conn.cursor()

cursor.execute("DELETE FROM sales")

conn.commit()
conn.close()

print("✅ Sales table cleared successfully!")