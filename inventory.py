import streamlit as st
import sqlite3
import pandas as pd

# Database connection
conn = sqlite3.connect(
    "data/bakery.db",
    check_same_thread=False
)

cursor = conn.cursor()

def show_inventory_page():

    st.header("Inventory Management")

    # =========================================
    # ADD NEW ITEM
    # =========================================

    st.subheader("Add New Inventory Item")

    with st.form("add_item_form"):

        item_name = st.text_input("Item Name")

        category = st.text_input("Category")

        quantity = st.number_input(
            "Initial Quantity",
            min_value=0.0
        )

        unit = st.text_input(
            "Unit (kg, pcs, liters etc)"
        )

        cost_per_unit = st.number_input(
            "Cost Per Unit",
            min_value=0.0
        )

        add_button = st.form_submit_button(
            "Add New Item"
        )

        if add_button:

            # Check duplicate item
            existing_item = pd.read_sql_query(f"""
            SELECT * FROM inventory
            WHERE item_name = '{item_name}'
            """, conn)

            if not existing_item.empty:

                st.error(
                    "Item already exists. "
                    "Use Restock section instead."
                )

            else:

                cursor.execute("""
                INSERT INTO inventory
                (item_name, category, quantity, unit, cost_per_unit)
                VALUES (?, ?, ?, ?, ?)
                """, (
                    item_name,
                    category,
                    quantity,
                    unit,
                    cost_per_unit
                ))

                conn.commit()

                st.success(
                    f"{item_name} added successfully!"
                )

    # =========================================
    # RESTOCK EXISTING ITEM
    # =========================================

    st.subheader("Restock Existing Item")

    inventory_df = pd.read_sql_query(
        "SELECT * FROM inventory",
        conn
    )

    if not inventory_df.empty:

        item_list = inventory_df[
            "item_name"
        ].tolist()

        with st.form("restock_form"):

            selected_item = st.selectbox(
                "Select Item",
                item_list
            )

            add_quantity = st.number_input(
                "Quantity to Add",
                min_value=0.0
            )

            restock_button = st.form_submit_button(
                "Restock Item"
            )

            if restock_button:

                current_item = pd.read_sql_query(f"""
                SELECT * FROM inventory
                WHERE item_name = '{selected_item}'
                """, conn)

                current_quantity = (
                    current_item.iloc[0]["quantity"]
                )

                new_quantity = (
                    current_quantity + add_quantity
                )

                cursor.execute("""
                UPDATE inventory
                SET quantity = ?
                WHERE item_name = ?
                """, (
                    new_quantity,
                    selected_item
                ))

                conn.commit()

                st.success(
                    f"{selected_item} restocked successfully!"
                )

    # =========================================
    # VIEW INVENTORY
    # =========================================

    st.subheader("Current Inventory")

    df = pd.read_sql_query(
        "SELECT * FROM inventory",
        conn
    )

    st.dataframe(df)

    # =========================================
    # DELETE ITEM
    # =========================================

    st.subheader("Delete Inventory Item")

    if not df.empty:

        item_ids = df["id"].tolist()

        selected_id = st.selectbox(
            "Select Item ID to Delete",
            item_ids
        )

        if st.button("Delete Item"):

            cursor.execute(
                "DELETE FROM inventory WHERE id = ?",
                (selected_id,)
            )

            conn.commit()

            st.warning(
                "Item Deleted Successfully!"
            )

            st.rerun()