import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect("data/inventory.db")

# Read aggregated demand
df = pd.read_sql(
    "SELECT * FROM daily_product_demand",
    conn
)

# Convert Date column
df["Date"] = pd.to_datetime(df["Date"])

all_dates = pd.date_range(
    df["Date"].min(),
    df["Date"].max()
)

cleaned = []

for product in df["Item"].unique():

    product_df = df[df["Item"] == product].copy()

    product_df = product_df.set_index("Date")

    # Only keep quantity column
    product_df = product_df[["quantity_sold"]]

    product_df = product_df.reindex(all_dates)

    # Fill missing sales with 0
    product_df["quantity_sold"] = (
        product_df["quantity_sold"]
        .fillna(0)
        .astype(int)
    )

    product_df = product_df.reset_index()

    product_df.rename(
        columns={"index": "Date"},
        inplace=True
    )

    product_df["Item"] = product

    cleaned.append(product_df)

clean_df = pd.concat(cleaned)

clean_df.to_sql(
    "daily_product_demand_clean",
    conn,
    if_exists="replace",
    index=False
)

conn.close()

print("✅ Clean daily demand table created successfully!")