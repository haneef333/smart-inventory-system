import streamlit as st
import sqlite3
import pandas as pd

# Database connection
conn = sqlite3.connect("data/bakery.db", check_same_thread=False)
cursor = conn.cursor()

def show_recipe_page():

    st.header("Recipe Management")

    # --------------------------------
    # GET INVENTORY ITEMS
    # --------------------------------

    inventory_df = pd.read_sql_query(
        "SELECT * FROM inventory",
        conn
    )

    ingredient_list = inventory_df["item_name"].tolist()

    # --------------------------------
    # ADD RECIPE
    # --------------------------------

    with st.form("recipe_form"):

        st.subheader("Add Recipe")

        product_name = st.text_input("Product Name")

        ingredient_name = st.selectbox(
            "Select Ingredient",
            ingredient_list
        )

        quantity_needed = st.number_input(
            "Quantity Needed",
            min_value=0.0
        )

        unit = st.text_input("Unit")

        submit_button = st.form_submit_button("Add Recipe")

        if submit_button:

            cursor.execute("""
            INSERT INTO recipes
            (product_name, ingredient_name, quantity_needed, unit)
            VALUES (?, ?, ?, ?)
            """, (
                product_name,
                ingredient_name,
                quantity_needed,
                unit
            ))

            conn.commit()

            st.success("Recipe Added Successfully!")

    # --------------------------------
    # VIEW RECIPES
    # --------------------------------

    st.subheader("Recipe List")

    recipe_df = pd.read_sql_query(
        "SELECT * FROM recipes",
        conn
    )

    st.dataframe(recipe_df)