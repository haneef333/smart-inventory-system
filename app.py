import os
import sqlite3

# Ensure data folder exists
os.makedirs("data", exist_ok=True)

# Ensure database and tables exist
if not os.path.exists("data/bakery.db"):
    import database  # this runs your table-creation script

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

    user = st.text_input("Username")
    pwd = st.text_input("Password", type="password")

    if st.button("Login"):
        if user == "admin" and pwd == "admin":
            st.session_state.logged_in = True
        else:
            st.error("Invalid credentials")

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
