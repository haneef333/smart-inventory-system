import streamlit as st
import sqlite3
import pandas as pd

# Database connection
conn = sqlite3.connect(
    "data/bakery.db",
    check_same_thread=False
)

def show_prediction_page():

    st.header("Smart Restock Predictions")

    # --------------------------------
    # LOAD DATA
    # --------------------------------

    usage_df = pd.read_sql_query(
        "SELECT * FROM ingredient_usage",
        conn
    )

    inventory_df = pd.read_sql_query(
        "SELECT * FROM inventory",
        conn
    )

    # --------------------------------
    # CHECK DATA EXISTS
    # --------------------------------

    if usage_df.empty:

        st.warning(
            "No ingredient usage data available yet."
        )

        return

    # --------------------------------
    # CALCULATE AVERAGE USAGE
    # --------------------------------

    avg_usage = usage_df.groupby(
        "ingredient_name"
    )["quantity_used"].mean().reset_index()

    avg_usage.columns = [
        "Ingredient",
        "Average Usage"
    ]

    # --------------------------------
    # PREDICT FUTURE REQUIREMENT
    # --------------------------------

    avg_usage["Recommended Stock"] = (
        avg_usage["Average Usage"] * 2
    )

    # --------------------------------
    # MERGE WITH INVENTORY
    # --------------------------------

    merged_df = pd.merge(
        avg_usage,
        inventory_df,
        left_on="Ingredient",
        right_on="item_name"
    )

    # --------------------------------
    # SHOW PREDICTIONS
    # --------------------------------

    st.subheader("Restock Recommendations")

    for _, row in merged_df.iterrows():

        ingredient = row["Ingredient"]

        current_stock = row["quantity"]

        recommended_stock = row[
            "Recommended Stock"
        ]

        st.write(f"Ingredient: {ingredient}")

        st.write(
            f"Current Stock: {current_stock}"
        )

        st.write(
            f"Recommended Stock: "
            f"{recommended_stock:.2f}"
        )

        if current_stock < recommended_stock:

            st.error(
                f"Restock {ingredient} soon!"
            )

        else:

            st.success(
                f"{ingredient} stock level is good."
            )

        st.divider()