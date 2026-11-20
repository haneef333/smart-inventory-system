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

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS tasks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        task_date TEXT NOT NULL,
        title TEXT NOT NULL,
        is_done INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS portfolio_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        image_filename TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # --- Orders placed by customers on the storefront (MERN app) ---
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS online_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        external_id TEXT NOT NULL UNIQUE,
        customer_name TEXT,
        customer_phone TEXT,
        customer_email TEXT,
        fulfilment TEXT DEFAULT 'pickup',
        address TEXT,
        due_date TEXT,
        time_slot TEXT,
        payment_method TEXT DEFAULT 'cash',
        payment_status TEXT DEFAULT 'unpaid',
        notes TEXT,
        delivery_fee REAL DEFAULT 0,
        coupon_code TEXT,
        discount REAL DEFAULT 0,
        total REAL DEFAULT 0,
        status TEXT DEFAULT 'new',
        status_note TEXT,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        decided_at TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        callback_state TEXT DEFAULT 'none',
        callback_attempts INTEGER DEFAULT 0,
        callback_error TEXT,
        callback_at TIMESTAMP
    )
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS online_order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        online_order_id INTEGER NOT NULL REFERENCES online_orders(id) ON DELETE CASCADE,
        product_name TEXT NOT NULL,
        display_name TEXT,
        quantity INTEGER NOT NULL,
        unit_price REAL NOT NULL,
        recipe_scale REAL DEFAULT 1,
        details TEXT,
        photo_url TEXT
    )
    """)

    conn.commit()
    _migrate_orders_columns(cursor, conn)
    # Databases created before cake options, coupons and time slots get the new columns
    _add_missing_columns(cursor, conn, "online_orders", {
        "time_slot": "TEXT", "coupon_code": "TEXT", "discount": "REAL DEFAULT 0",
    })
    _add_missing_columns(cursor, conn, "online_order_items", {
        "recipe_scale": "REAL DEFAULT 1", "details": "TEXT", "photo_url": "TEXT",
    })
    conn.close()


def _add_missing_columns(cursor, conn, table, columns):
    existing = {row[1] for row in cursor.execute(f"PRAGMA table_info({table})").fetchall()}
    for name, col_type in columns.items():
        if name not in existing:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {name} {col_type}")
    conn.commit()


def _migrate_orders_columns(cursor, conn):
    """Add bakery-workflow columns to a pre-existing orders table, if missing."""
    cursor.execute("PRAGMA table_info(orders)")
    existing_cols = {row["name"] for row in cursor.fetchall()}

    new_cols = {
        "customer_name": "TEXT",
        "due_date": "TEXT",
        "delivery_status": "TEXT DEFAULT 'pending'",
        "payment_status": "TEXT DEFAULT 'unpaid'",
        "payment_method": "TEXT DEFAULT 'cash'",
        # Links an order row back to the storefront order it came from (NULL for walk-in orders)
        "online_order_id": "INTEGER",
    }

    for col_name, col_def in new_cols.items():
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE orders ADD COLUMN {col_name} {col_def}")

    conn.commit()
