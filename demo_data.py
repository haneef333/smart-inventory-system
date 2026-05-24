import sqlite3
import random
from datetime import datetime, timedelta

# Database connection
conn = sqlite3.connect("data/bakery.db")

cursor = conn.cursor()

# --------------------------------
# SAMPLE PRODUCTS
# --------------------------------

products = [
    {
        "name": "Chocolate Cake",
        "price": 1000,
        "cost": 500
    },
    {
        "name": "Brownie",
        "price": 200,
        "cost": 80
    },
    {
        "name": "Cupcake",
        "price": 150,
        "cost": 60
    }
]

# --------------------------------
# GENERATE 90 DAYS DATA
# --------------------------------

for day in range(90):

    current_date = (
        datetime.now() - timedelta(days=day)
    )

    # More orders on weekends
    weekday = current_date.weekday()

    if weekday in [5, 6]:
        orders_count = random.randint(8, 15)
    else:
        orders_count = random.randint(3, 8)

    # --------------------------------
    # CREATE ORDERS
    # --------------------------------

    for _ in range(orders_count):

        product = random.choice(products)

        quantity = random.randint(1, 5)

        revenue = (
            product["price"] * quantity
        )

        cost = (
            product["cost"] * quantity
        )

        profit = revenue - cost

        # --------------------------------
        # INSERT ORDER
        # --------------------------------

        cursor.execute("""
        INSERT INTO orders
        (product_name, quantity, selling_price, order_date)
        VALUES (?, ?, ?, ?)
        """, (
            product["name"],
            quantity,
            product["price"],
            current_date
        ))

        # --------------------------------
        # INSERT SALES
        # --------------------------------

        cursor.execute("""
        INSERT INTO sales
        (product_name, revenue, cost, profit, sale_date)
        VALUES (?, ?, ?, ?, ?)
        """, (
            product["name"],
            revenue,
            cost,
            profit,
            current_date
        ))

# --------------------------------
# SAVE CHANGES
# --------------------------------

conn.commit()

conn.close()

print("Demo business data generated successfully!")