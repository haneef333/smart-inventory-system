import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, SCRIPT_DIR)
os.chdir(SCRIPT_DIR)

import cmdstanpy

CMDSTAN_MARKER = "/tmp/.cmdstan_installed"

if not os.path.exists(CMDSTAN_MARKER):
    cmdstanpy.install_cmdstan()
    with open(CMDSTAN_MARKER, "w") as f:
        f.write("done")

import sqlite3

os.makedirs("data", exist_ok=True)

DB_PATH = "data/inventory.db"


def table_exists(cursor, table_name):
    cursor.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
        (table_name,)
    )
    return cursor.fetchone() is not None


# --------------------------------
# OPEN DB, SELF-HEAL IF CORRUPTED
# --------------------------------
try:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("SELECT 1")
except sqlite3.DatabaseError:
    conn.close()
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)

conn.close()

# --------------------------------
# ALWAYS ENSURE BASE SCHEMA EXISTS
# --------------------------------
import database

# --------------------------------
# RE-OPEN AFTER database.py
# (it manages its own connection/commit/close)
# --------------------------------
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# --------------------------------
# DEMO SALES DATA
# --------------------------------
needs_demo_data = (
    not table_exists(cursor, "sales")
    or cursor.execute("SELECT COUNT(*) FROM sales").fetchone()[0] == 0
)

if needs_demo_data:
    import generate_demo_data

# --------------------------------
# REAL DEMAND-FORECAST DATA
# --------------------------------
if not table_exists(cursor, "daily_product_demand_clean"):
    import import_real_data
    import prepare_daily_demand
    import clean_daily_demand

# --------------------------------
# SEED REAL PRODUCTS / INGREDIENTS / RECIPES
# --------------------------------
needs_product_seed = (
    not table_exists(cursor, "inventory")
    or cursor.execute(
        "SELECT id FROM inventory WHERE item_name = 'Wheat Flour'"
    ).fetchone() is None
)

if needs_product_seed:
    import seed_products

conn.close()

# --------------------------------
# STREAMLIT APP
# --------------------------------
import streamlit as st
from dashboard import show_dashboard_page
from inventory import show_inventory_page
from recipes import show_recipe_page
from orders import show_order_page
from ml_forecast import show_ml_forecast_page

# -------------------------------
# PAGE CONFIG
# -------------------------------
st.set_page_config(
    page_title="Smart Inventory System",
    layout="wide"
)

# -------------------------------
# LOGIN SYSTEM (SIMPLE DEMO)
# -------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False


def login():
    st.title("🔐 Login")
    st.info("👉 Demo credentials — Username: **admin**  Password: **admin**")

    user = st.text_input("Username", value="admin")
    pwd = st.text_input("Password", type="password", value="admin")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login"):
            if user == "admin" and pwd == "admin":
                st.session_state.logged_in = True
            else:
                st.error("Invalid credentials")
    with col2:
        if st.button("Continue as Guest"):
            st.session_state.logged_in = True


if not st.session_state.logged_in:
    login()
    st.stop()

# -------------------------------
# THEME TOGGLE
# -------------------------------
if "theme" not in st.session_state:
    st.session_state.theme = "dark"

if st.sidebar.button("🌓 Toggle Theme"):
    st.session_state.theme = (
        "light" if st.session_state.theme == "dark" else "dark"
    )

# -------------------------------
# SIDEBAR NAVIGATION (WITH ICONS)
# -------------------------------
menu = st.sidebar.radio(
    "📌 Navigation",
    [
        "📊 Dashboard",
        "📦 Inventory",
        "📖 Recipes",
        "🧾 Orders",
        "📈 Forecast"
    ]
)

# -------------------------------
# ROUTING
# -------------------------------
if menu == "📊 Dashboard":
    show_dashboard_page()

elif menu == "📦 Inventory":
    show_inventory_page()

elif menu == "📖 Recipes":
    show_recipe_page()

elif menu == "🧾 Orders":
    show_order_page()

elif menu == "📈 Forecast":
    show_ml_forecast_page()