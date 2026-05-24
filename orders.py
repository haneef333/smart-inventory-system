import streamlit as st
import sqlite3
import pandas as pd

# Database connection
conn = sqlite3.connect("data/bakery.db", check_same_thread=False)
cursor = conn.cursor()

def show_order_page():

    st.header("Order Processing")

    # --------------------------------
    # GET PRODUCTS
    # --------------------------------

    recipe_df = pd.read_sql_query(
        "SELECT DISTINCT product_name FROM recipes",
        conn
    )

    product_list = recipe_df["product_name"].tolist()

    # --------------------------------
    # ORDER FORM
    # --------------------------------

    with st.form("order_form"):

        product_name = st.selectbox(
            "Select Product",
            product_list
        )

        order_quantity = st.number_input(
            "Quantity Ordered",
            min_value=1,
            step=1
        )

        selling_price = st.number_input(
            "Selling Price",
            min_value=0.0
        )

        submit_button = st.form_submit_button("Place Order")

        # --------------------------------
        # PROCESS ORDER
        # --------------------------------

        if submit_button:

            # Get recipe ingredients
            ingredients_df = pd.read_sql_query(f"""
            SELECT * FROM recipes
            WHERE product_name = '{product_name}'
            """, conn)

            total_cost = 0

            # --------------------------------
            # CHECK STOCK AVAILABILITY
            # --------------------------------

            insufficient_stock = False

            for _, row in ingredients_df.iterrows():

                ingredient = row["ingredient_name"]

                quantity_needed = (
                    row["quantity_needed"] * order_quantity
                )

                inventory_item = pd.read_sql_query(f"""
                SELECT * FROM inventory
                WHERE item_name = '{ingredient}'
                """, conn)

                current_quantity = inventory_item.iloc[0]["quantity"]

                # Check stock
                if current_quantity < quantity_needed:

                    st.error(
                        f"Not enough stock for {ingredient}. "
                        f"Available: {current_quantity}"
                    )

                    insufficient_stock = True

            # --------------------------------
            # PROCESS ORDER ONLY IF STOCK OK
            # --------------------------------

            if not insufficient_stock:

                for _, row in ingredients_df.iterrows():

                    ingredient = row["ingredient_name"]

                    quantity_needed = (
                        row["quantity_needed"] * order_quantity
                    )

                    inventory_item = pd.read_sql_query(f"""
                    SELECT * FROM inventory
                    WHERE item_name = '{ingredient}'
                    """, conn)

                    current_quantity = inventory_item.iloc[0]["quantity"]

                    cost_per_unit = inventory_item.iloc[0]["cost_per_unit"]

                    # Calculate new stock
                    new_quantity = (
                        current_quantity - quantity_needed
                    )

                    # Update inventory
                    cursor.execute("""
                    UPDATE inventory
                    SET quantity = ?
                    WHERE item_name = ?
                    """, (
                        new_quantity,
                        ingredient
                    ))

                    # Calculate ingredient cost
                    ingredient_cost = (
                        quantity_needed * cost_per_unit
                    )

                    total_cost += ingredient_cost

                    # --------------------------------
                    # SAVE INGREDIENT USAGE
                    # --------------------------------

                    cursor.execute("""
                    INSERT INTO ingredient_usage
                    (ingredient_name, quantity_used)
                    VALUES (?, ?)
                    """, (
                        ingredient,
                        quantity_needed
                    ))

                # --------------------------------
                # REVENUE & PROFIT
                # --------------------------------

                revenue = (
                    selling_price * order_quantity
                )

                profit = revenue - total_cost

                # --------------------------------
                # SAVE ORDER
                # --------------------------------

                cursor.execute("""
                INSERT INTO orders
                (product_name, quantity, selling_price)
                VALUES (?, ?, ?)
                """, (
                    product_name,
                    order_quantity,
                    selling_price
                ))

                # --------------------------------
                # SAVE SALES DATA
                # --------------------------------

                cursor.execute("""
                INSERT INTO sales
                (product_name, revenue, cost, profit)
                VALUES (?, ?, ?, ?)
                """, (
                    product_name,
                    revenue,
                    total_cost,
                    profit
                ))

                conn.commit()

                st.success("Order Processed Successfully!")

                st.write(f"Total Cost: ₹{total_cost:.2f}")
                st.write(f"Revenue: ₹{revenue:.2f}")
                st.write(f"Profit: ₹{profit:.2f}")

    # --------------------------------
    # ORDER HISTORY
    # --------------------------------

    st.subheader("Order History")

    orders_df = pd.read_sql_query(
        "SELECT * FROM orders",
        conn
    )

    st.dataframe(orders_df)