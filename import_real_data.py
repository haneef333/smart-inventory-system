import sqlite3
import pandas as pd

# Load Kaggle dataset
df = pd.read_csv("BreadBasket_DMS.csv")

# Connect to database
conn = sqlite3.connect("data/bakery.db")

# Save dataset into a new table
df.to_sql(
    "bakery_transactions",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("✅ Real bakery dataset imported successfully!")