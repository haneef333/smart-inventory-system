import sqlite3
import pandas as pd

conn = sqlite3.connect("data/inventory.db")

df = pd.read_sql("""
SELECT
    Item,
    SUM(quantity_sold) AS total_sales
FROM daily_product_demand_clean
GROUP BY Item
ORDER BY total_sales DESC
LIMIT 20
""", conn)

print(df)

conn.close()