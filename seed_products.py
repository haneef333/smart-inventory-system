"""
Seed Products Script

Adds generic reusable ingredients to the Inventory table and creates
matching Recipes for 18 real bakery products found in the imported
Kaggle dataset (daily_product_demand_clean).

This connects the Forecast page (real CSV-driven product names) to the
Inventory/Recipes/Orders pages, so ordering "Bread" through the app
actually deducts stock and matches what the Forecast page predicts
for "Bread".

Safe to run multiple times — skips items/recipes that already exist.
"""

import sqlite3

conn = sqlite3.connect("data/inventory.db")
cursor = conn.cursor()

# --------------------------------
# GENERIC INGREDIENTS (reusable across products)
# --------------------------------

ingredients = [
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

for name, category, qty, unit, cost, threshold in ingredients:
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
            (name, category, qty, unit, cost, threshold)
        )

conn.commit()
print(f"✅ Seeded {len(ingredients)} ingredients (skipped any that already existed).")

# --------------------------------
# RECIPES (product -> ingredient -> quantity per unit sold)
# --------------------------------

recipes = {
    "Bread": [
        ("Wheat Flour", 400, "g"),
        ("Yeast", 8, "g"),
        ("Salt", 6, "g"),
        ("Sugar", 10, "g"),
    ],
    "Cake": [
        ("Wheat Flour", 300, "g"),
        ("Sugar", 200, "g"),
        ("Butter", 150, "g"),
        ("Eggs", 3, "pcs"),
        ("Baking Powder", 5, "g"),
    ],
    "Cookies": [
        ("Wheat Flour", 150, "g"),
        ("Sugar", 80, "g"),
        ("Butter", 70, "g"),
        ("Eggs", 1, "pcs"),
        ("Chocolate Chips", 40, "g"),
    ],
    "Muffin": [
        ("Wheat Flour", 120, "g"),
        ("Sugar", 60, "g"),
        ("Butter", 40, "g"),
        ("Eggs", 1, "pcs"),
        ("Baking Powder", 4, "g"),
    ],
    "Brownie": [
        ("Wheat Flour", 100, "g"),
        ("Sugar", 120, "g"),
        ("Butter", 100, "g"),
        ("Cocoa Powder", 60, "g"),
        ("Eggs", 2, "pcs"),
    ],
    "Scone": [
        ("Wheat Flour", 150, "g"),
        ("Butter", 60, "g"),
        ("Milk", 50, "ml"),
        ("Sugar", 30, "g"),
        ("Baking Powder", 5, "g"),
    ],
    "Medialuna": [
        ("Wheat Flour", 100, "g"),
        ("Butter", 50, "g"),
        ("Sugar", 20, "g"),
        ("Yeast", 4, "g"),
        ("Milk", 30, "ml"),
    ],
    "Pastry": [
        ("Wheat Flour", 120, "g"),
        ("Butter", 80, "g"),
        ("Sugar", 25, "g"),
        ("Eggs", 1, "pcs"),
    ],
    "Farm House": [
        ("Wheat Flour", 350, "g"),
        ("Yeast", 7, "g"),
        ("Milk", 40, "ml"),
        ("Salt", 5, "g"),
    ],
    "Fudge": [
        ("Sugar", 200, "g"),
        ("Butter", 100, "g"),
        ("Milk", 80, "ml"),
        ("Cocoa Powder", 40, "g"),
    ],
    "Coffee": [
        ("Coffee Beans", 18, "g"),
        ("Milk", 100, "ml"),
        ("Sugar", 10, "g"),
    ],
    "Tea": [
        ("Tea Leaves", 5, "g"),
        ("Milk", 50, "ml"),
        ("Sugar", 8, "g"),
    ],
    "Hot chocolate": [
        ("Cocoa Solids (Hot Chocolate Mix)", 30, "g"),
        ("Milk", 150, "ml"),
        ("Sugar", 15, "g"),
    ],
    "Baguette": [
        ("Wheat Flour", 300, "g"),
        ("Yeast", 6, "g"),
        ("Salt", 6, "g"),
    ],
    "Toast": [
        ("Wheat Flour", 200, "g"),
        ("Butter", 20, "g"),
        ("Yeast", 4, "g"),
    ],
    "Bakewell": [
        ("Wheat Flour", 120, "g"),
        ("Butter", 70, "g"),
        ("Sugar", 60, "g"),
        ("Almonds", 40, "g"),
        ("Jam / Fruit Filling", 30, "g"),
    ],
    "Victorian Sponge": [
        ("Wheat Flour", 200, "g"),
        ("Sugar", 150, "g"),
        ("Butter", 150, "g"),
        ("Eggs", 3, "pcs"),
        ("Jam / Fruit Filling", 50, "g"),
        ("Cream Cheese", 40, "g"),
    ],
    "Bread Pudding": [
        ("Wheat Flour", 100, "g"),
        ("Milk", 200, "ml"),
        ("Eggs", 2, "pcs"),
        ("Sugar", 60, "g"),
        ("Cinnamon", 3, "g"),
    ],
}

recipes_added = 0

for product_name, ingredient_list in recipes.items():

    existing = cursor.execute(
        "SELECT id FROM recipes WHERE product_name = ?", (product_name,)
    ).fetchone()

    if existing:
        continue

    for ingredient_name, quantity_needed, unit in ingredient_list:
        cursor.execute(
            """
            INSERT INTO recipes
            (product_name, ingredient_name, quantity_needed, unit)
            VALUES (?, ?, ?, ?)
            """,
            (product_name, ingredient_name, quantity_needed, unit)
        )

    recipes_added += 1

conn.commit()
conn.close()

print(f"✅ Seeded recipes for {recipes_added} products (skipped any that already existed).")
print("Done. Inventory, Recipes, Orders, and Forecast now share the same product names.")