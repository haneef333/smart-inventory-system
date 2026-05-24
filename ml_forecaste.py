import streamlit as st
import sqlite3
import pandas as pd

conn = sqlite3.connect("data/bakery.db", check_same_thread=False)

def show_ml_forecast_page():

    st.header("Smart Demand Forecasting (Improved ML)")

    # Load sales data
    sales_df = pd.read_sql_query("SELECT * FROM sales", conn)

    if sales_df.empty:
        st.warning("No sales data available.")
        return

    # Convert date
    sales_df["sale_date"] = pd.to_datetime(sales_df["sale_date"], errors="coerce")
    sales_df = sales_df.dropna(subset=["sale_date"])

    sales_df["date"] = sales_df["sale_date"].dt.date

    # Select product
    products = sales_df["product_name"].unique()

    selected_product = st.selectbox("Select Product", products)

    product_df = sales_df[sales_df["product_name"] == selected_product]

    # Group daily sales
    daily_sales = product_df.groupby("date")["profit"].count().reset_index()
    daily_sales.columns = ["date", "orders"]

    if len(daily_sales) < 3:
        st.warning("Not enough data for forecasting.")
        return

    # Moving average (last 3 days / last 7 days logic)
    window = min(3, len(daily_sales))

    daily_sales["rolling_avg"] = daily_sales["orders"].rolling(window).mean()

    predicted = daily_sales["rolling_avg"].iloc[-1]

    if pd.isna(predicted):
        predicted = daily_sales["orders"].mean()

    # Output
    st.subheader("Forecast Result")

    st.success(
        f"Predicted demand for '{selected_product}' tomorrow: {round(predicted, 2)} orders"
    )

    st.subheader("Historical Trend")

    st.line_chart(daily_sales.set_index("date")["orders"])