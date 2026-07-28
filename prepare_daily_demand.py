import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("data/inventory.db")

# Read transaction data
df = pd.read_sql(
    "SELECT Date, Item FROM bakery_transactions",
    conn
)

# Count how many of each item was sold per day
daily_demand = (
    df.groupby(["Date", "Item"])
      .size()
      .reset_index(name="quantity_sold")
)

# Save into SQLite
daily_demand.to_sql(
    "daily_product_demand",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("✅ Daily demand table created successfully!")