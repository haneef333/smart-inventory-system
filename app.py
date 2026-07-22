import os
import sqlite3

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Always ensure tables exist (safe — uses CREATE TABLE IF NOT EXISTS)
import database

# Populate with demo data if sales table is empty
conn_check = sqlite3.connect("data/bakery.db")
cursor_check = conn_check.cursor()
cursor_check.execute("SELECT COUNT(*) FROM sales")
sales_count = cursor_check.fetchone()[0]
conn_check.close()

if sales_count == 0:
    import demo_data  # placeholder — will confirm correct script name below

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
        "🍰 Recipes",
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

elif menu == "🍰 Recipes":
    show_recipe_page()

elif menu == "🧾 Orders":
    show_order_page()

elif menu == "📈 Forecast":
    show_ml_forecast_page()
