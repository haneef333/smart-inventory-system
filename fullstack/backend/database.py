import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "inventory.db")

os.makedirs(DATA_DIR, exist_ok=True)


def get_connection():
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,),
    )
    return cursor.fetchone() is not None


def init_schema():
    """Create base tables if they don't already exist. Safe to call repeatedly."""
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS inventory (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        item_name TEXT NOT NULL UNIQUE,
        category TEXT,
        quantity REAL,
        unit TEXT,
        cost_per_unit REAL,
        reorder_threshold REAL DEFAULT 10
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS recipes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        ingredient_name TEXT NOT NULL,
        quantity_needed REAL,
        unit TEXT
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        product_name TEXT NOT NULL,
        quantity INTEGER,
        selling_price REAL,
        order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        customer_name TEXT,
        due_date TEXT,
        delivery_status TEXT DEFAULT 'pending',
        payment_status TEXT DEFAULT 'unpaid'
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT NOT NULL,
        category TEXT NOT NULL,
        amount REAL NOT NULL,
        expense_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS ingredient_usage (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ingredient_name TEXT,
        quantity_used REAL,
        usage_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    _migrate_orders_columns(cursor, conn)
    conn.close()


def _migrate_orders_columns(cursor, conn):
    """Add bakery-workflow columns to a pre-existing orders table, if missing."""
    cursor.execute("PRAGMA table_info(orders)")
    existing_cols = {row["name"] for row in cursor.fetchall()}

    new_cols = {
        "customer_name": "TEXT",
        "due_date": "TEXT",
        "delivery_status": "TEXT DEFAULT 'pending'",
        "payment_status": "TEXT DEFAULT 'unpaid'",
    }

    for col_name, col_def in new_cols.items():
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_def}")

    conn.commit()
