import sqlite3

# Connect to database
conn = sqlite3.connect("data/bakery.db")

# Create cursor
cursor = conn.cursor()

# --------------------------------
# INVENTORY TABLE
# --------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS inventory (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_name TEXT NOT NULL,
    category TEXT,
    quantity REAL,
    unit TEXT,
    cost_per_unit REAL
)
""")

# --------------------------------
# RECIPES TABLE
# --------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS recipes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    ingredient_name TEXT NOT NULL,
    quantity_needed REAL,
    unit TEXT
)
""")

# --------------------------------
# ORDERS TABLE
# --------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS orders (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    quantity INTEGER,
    selling_price REAL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# --------------------------------
# SALES TABLE
# --------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS sales (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT,
    revenue REAL,
    cost REAL,
    profit REAL,
    sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# --------------------------------
# INGREDIENT USAGE TABLE
# --------------------------------

cursor.execute("""
CREATE TABLE IF NOT EXISTS ingredient_usage (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ingredient_name TEXT,
    quantity_used REAL,
    usage_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

# Save changes
conn.commit()

# Close connection
conn.close()

print("Database and tables created successfully!")