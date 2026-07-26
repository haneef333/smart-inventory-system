import sqlite3
import pandas as pd

conn = sqlite3.connect("data/bakery.db")

df = pd.read_sql(
    "SELECT * FROM daily_product_demand_clean LIMIT 20",
    conn
)

print(df)

conn.close()