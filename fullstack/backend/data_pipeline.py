"""
Self-seeding data pipeline. Mirrors the logic from the original Streamlit
prototype, adapted to run once at API startup so a fresh clone works with
zero manual setup.
"""

import os
import random
from datetime import datetime, timedelta

import pandas as pd

from database import get_connection, table_exists, DATA_DIR

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_PATH = os.path.join(BASE_DIR, "BreadBasket_DMS.csv")


def generate_demo_sales():
    """Synthetic orders/sales for the dashboard demo. Not used for forecasting."""
    conn = get_connection()
    cursor = conn.cursor()

    products = [
        {"name": "Chocolate Cake", "price": 1000, "cost": 500},
        {"name": "Brownie", "price": 200, "cost": 80},
        {"name": "Cupcake", "price": 150, "cost": 60},
    ]

    for day in range(90):
        current_date = datetime.now() - timedelta(days=day)
        weekday = current_date.weekday()
        orders_count = random.randint(8, 15) if weekday in (5, 6) else random.randint(3, 8)

        for _ in range(orders_count):
            product = random.choice(products)
            qty = random.randint(1, 4)
            revenue = product["price"] * qty
            cost = product["cost"] * qty
            profit = revenue - cost

            cursor.execute(
                """
                INSERT INTO orders (product_name, quantity, selling_price, order_date)
                VALUES (?, ?, ?, ?)
                """,
                (product["name"], qty, product["price"], current_date),
            )

            cursor.execute(
                """
                INSERT INTO sales (product_name, revenue, cost, profit, sale_date)
                VALUES (?, ?, ?, ?, ?)
                """,
                (product["name"], revenue, cost, profit, current_date),
            )

    conn.commit()
    conn.close()


def import_real_data():
    df = pd.read_csv(CSV_PATH)
    conn = get_connection()
    df.to_sql("bakery_transactions", conn, if_exists="replace", index=False)
    conn.close()


def prepare_daily_demand():
    conn = get_connection()
    df = pd.read_sql("SELECT Date, Item FROM bakery_transactions", conn)

    daily_demand = (
        df.groupby(["Date", "Item"]).size().reset_index(name="quantity_sold")
    )

    daily_demand.to_sql("daily_product_demand", conn, if_exists="replace", index=False)
    conn.close()


def clean_daily_demand():
    conn = get_connection()
    df = pd.read_sql("SELECT * FROM daily_product_demand", conn)
    df["Date"] = pd.to_datetime(df["Date"])

    all_dates = pd.date_range(df["Date"].min(), df["Date"].max())
    cleaned = []

    for product in df["Item"].unique():
        product_df = df[df["Item"] == product].copy().set_index("Date")
        product_df = product_df[["quantity_sold"]]
        product_df = product_df.reindex(all_dates)
        product_df["quantity_sold"] = product_df["quantity_sold"].fillna(0).astype(int)
        product_df = product_df.reset_index().rename(columns={"index": "Date"})
        product_df["Item"] = product
        cleaned.append(product_df)

    clean_df = pd.concat(cleaned)
    clean_df.to_sql("daily_product_demand_clean", conn, if_exists="replace", index=False)
    conn.close()


INGREDIENTS = [
    ("Wheat Flour", "Raw Material", 20000, "g", 0.06, 3000),
    ("Sugar", "Raw Material", 15000, "g", 0.05, 2000),
    ("Salt", "Raw Material", 5000, "g", 0.02, 500),
    ("Butter", "Dairy", 10000, "g", 0.5, 1500),
    ("Milk", "Dairy", 15000, "ml", 0.06, 2000),
    ("Eggs", "Dairy", 300, "pcs", 8, 40),
    ("Cocoa Powder", "Raw Material", 5000, "g", 0.8, 800),
    ("Yeast", "Raw Material", 1000, "g", 1.2, 150),
    ("Baking Powder", "Raw Material", 1000, "g", 0.9, 150),
    ("Vanilla Extract", "Flavoring", 1000, "ml", 2.5, 150),
    ("Cinnamon", "Spice", 500, "g", 3.0, 100),
    ("Coffee Beans", "Raw Material", 5000, "g", 1.5, 800),
    ("Tea Leaves", "Raw Material", 3000, "g", 1.2, 500),
    ("Cocoa Solids (Hot Chocolate Mix)", "Raw Material", 3000, "g", 1.0, 500),
    ("Almonds", "Raw Material", 4000, "g", 1.8, 600),
    ("Cream Cheese", "Dairy", 4000, "g", 0.9, 600),
    ("Jam / Fruit Filling", "Raw Material", 3000, "g", 1.1, 500),
    ("Chocolate Chips", "Raw Material", 4000, "g", 1.3, 600),
]

RECIPES = {
    "Bread": [("Wheat Flour", 400, "g"), ("Yeast", 8, "g"), ("Salt", 6, "g"), ("Sugar", 10, "g")],
    "Cake": [("Wheat Flour", 300, "g"), ("Sugar", 200, "g"), ("Butter", 150, "g"), ("Eggs", 3, "pcs"), ("Baking Powder", 5, "g")],
    "Cookies": [("Wheat Flour", 150, "g"), ("Sugar", 80, "g"), ("Butter", 70, "g"), ("Eggs", 1, "pcs"), ("Chocolate Chips", 40, "g")],
    "Muffin": [("Wheat Flour", 120, "g"), ("Sugar", 60, "g"), ("Butter", 40, "g"), ("Eggs", 1, "pcs"), ("Baking Powder", 4, "g")],
    "Brownie": [("Wheat Flour", 100, "g"), ("Sugar", 120, "g"), ("Butter", 100, "g"), ("Cocoa Powder", 60, "g"), ("Eggs", 2, "pcs")],
    "Scone": [("Wheat Flour", 150, "g"), ("Butter", 60, "g"), ("Milk", 50, "ml"), ("Sugar", 30, "g"), ("Baking Powder", 5, "g")],
    "Medialuna": [("Wheat Flour", 100, "g"), ("Butter", 50, "g"), ("Sugar", 20, "g"), ("Yeast", 4, "g"), ("Milk", 30, "ml")],
    "Pastry": [("Wheat Flour", 120, "g"), ("Butter", 80, "g"), ("Sugar", 25, "g"), ("Eggs", 1, "pcs")],
    "Farm House": [("Wheat Flour", 350, "g"), ("Yeast", 7, "g"), ("Milk", 40, "ml"), ("Salt", 5, "g")],
    "Fudge": [("Sugar", 200, "g"), ("Butter", 100, "g"), ("Milk", 80, "ml"), ("Cocoa Powder", 40, "g")],
    "Coffee": [("Coffee Beans", 18, "g"), ("Milk", 100, "ml"), ("Sugar", 10, "g")],
    "Tea": [("Tea Leaves", 5, "g"), ("Milk", 50, "ml"), ("Sugar", 8, "g")],
    "Hot chocolate": [("Cocoa Solids (Hot Chocolate Mix)", 30, "g"), ("Milk", 150, "ml"), ("Sugar", 15, "g")],
    "Baguette": [("Wheat Flour", 300, "g"), ("Yeast", 6, "g"), ("Salt", 6, "g")],
    "Toast": [("Wheat Flour", 200, "g"), ("Butter", 20, "g"), ("Yeast", 4, "g")],
    "Bakewell": [("Wheat Flour", 120, "g"), ("Butter", 70, "g"), ("Sugar", 60, "g"), ("Almonds", 40, "g"), ("Jam / Fruit Filling", 30, "g")],
    "Victorian Sponge": [("Wheat Flour", 200, "g"), ("Sugar", 150, "g"), ("Butter", 150, "g"), ("Eggs", 3, "pcs"), ("Jam / Fruit Filling", 50, "g"), ("Cream Cheese", 40, "g")],
    "Bread Pudding": [("Wheat Flour", 100, "g"), ("Milk", 200, "ml"), ("Eggs", 2, "pcs"), ("Sugar", 60, "g"), ("Cinnamon", 3, "g")],
}


def seed_products():
    conn = get_connection()
    cursor = conn.cursor()

    for name, category, qty, unit, cost, threshold in INGREDIENTS:
        existing = cursor.execute(
            "SELECT id FROM inventory WHERE item_name = ?", (name,)
        ).fetchone()
        if not existing:
            cursor.execute(
                """
                INSERT INTO inventory
                (item_name, category, quantity, unit, cost_per_unit, reorder_threshold)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (name, category, qty, unit, cost, threshold),
            )

    for product_name, ingredient_list in RECIPES.items():
        existing = cursor.execute(
            "SELECT id FROM recipes WHERE product_name = ?", (product_name,)
        ).fetchone()
        if existing:
            continue
        for ingredient_name, quantity_needed, unit in ingredient_list:
            cursor.execute(
                """
                INSERT INTO recipes (product_name, ingredient_name, quantity_needed, unit)
                VALUES (?, ?, ?, ?)
                """,
                (product_name, ingredient_name, quantity_needed, unit),
            )

    conn.commit()
    conn.close()


def run_startup_pipeline():
    """Idempotent: only does work that hasn't been done yet."""
    conn = get_connection()
    cursor = conn.cursor()

    needs_demo_data = (
        not table_exists(cursor, "sales")
        or cursor.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0
    )
    if needs_demo_data:
        generate_demo_sales()

    if not table_exists(cursor, "daily_product_demand_clean"):
        import_real_data()
        prepare_daily_demand()
        clean_daily_demand()

    needs_product_seed = (
        not table_exists(cursor, "inventory")
        or cursor.execute(
            "SELECT id FROM inventory WHERE item_name = 'Wheat Flour'"
        ).fetchone() is None
    )
    if needs_product_seed:
        seed_products()

    conn.close()
