import sqlite3
import random
from datetime import datetime, timedelta

# -------------------------------
# DATABASE CONNECTION
# -------------------------------
conn = sqlite3.connect("data/bakery.db")
cursor = conn.cursor()

# -------------------------------
# PRODUCTS
# -------------------------------
products = [
    ("Chocolate Cake", 500, 180),
    ("Vanilla Cake", 450, 150),
    ("Black Forest Cake", 700, 250),
    ("Cupcake", 80, 30),
    ("Brownie", 120, 45),
    ("Cookies", 60, 20),
    ("Donut", 50, 18),
    ("Croissant", 90, 35),
    ("Cheese Cake", 650, 240),
    ("Muffin", 70, 25)
]

# -------------------------------
# GENERATE 500 SALES
# -------------------------------
for _ in range(500):

    product = random.choice(products)

    product_name = product[0]
    selling_price = product[1]
    cost_price = product[2]

    qty = random.randint(1, 5)

    revenue = selling_price * qty
    profit = (selling_price - cost_price) * qty

    # -------------------------------
    # RANDOM DATE OVER LAST 60 DAYS
    # -------------------------------
    random_days = random.randint(0, 60)

    random_date = (
        datetime.now() - timedelta(days=random_days)
    ).strftime("%Y-%m-%d")

    # -------------------------------
    # INSERT
    # -------------------------------
    cursor.execute(
        """
        INSERT INTO sales
        (
            product_name,
            revenue,
            profit,
            sale_date
        )
        VALUES (?, ?, ?, ?)
        """,
        (
            product_name,
            revenue,
            profit,
            random_date
        )
    )

# -------------------------------
# SAVE
# -------------------------------
conn.commit()
conn.close()

print("✅ 500 realistic sales inserted!")