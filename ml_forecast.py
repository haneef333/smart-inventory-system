import streamlit as st
import sqlite3
import pandas as pd

from prophet import Prophet

conn = sqlite3.connect("data/bakery.db", check_same_thread=False)

def show_ml_forecast_page():

    st.header("Advanced Demand Forecasting (Prophet Model)")

    # Load data
    sales_df = pd.read_sql_query("SELECT * FROM sales", conn)

    if sales_df.empty:
        st.warning("No sales data available.")
        return

    # Convert date
    sales_df["sale_date"] = pd.to_datetime(
        sales_df["sale_date"],
        errors="coerce"
    )

    sales_df = sales_df.dropna(subset=["sale_date"])

    # Product selection
    products = sales_df["product_name"].unique()
    selected_product = st.selectbox("Select Product", products)

    product_df = sales_df[
        sales_df["product_name"] == selected_product
    ]

    # Prepare daily demand
    daily = product_df.groupby("sale_date").size().reset_index()
    daily.columns = ["ds", "y"]

    if len(daily) < 10:
        st.warning("Need at least 10 days of data for Prophet forecasting.")
        return

    # --------------------------------
    # PROPHET MODEL
    # --------------------------------

    try:

        model = Prophet()

        model.fit(daily)

        future = model.make_future_dataframe(periods=1)

        forecast = model.predict(future)

        predicted = forecast["yhat"].iloc[-1]

        # Trend logic
        last_actual = daily["y"].iloc[-1]

        if predicted > last_actual:
            trend = "Increasing 📈"
        else:
            trend = "Decreasing 📉"

        # Output
        st.subheader("Forecast Result")

        st.success(
            f"""
            Product: {selected_product}  
            Predicted Demand (Tomorrow): {round(predicted, 2)} orders  
            Trend: {trend}
            """
        )

        # Show forecast plot
        st.subheader("Forecast Visualization")

        fig = model.plot(forecast)

        st.pyplot(fig)

        # Show data
        st.subheader("Historical Data")

        st.line_chart(daily.set_index("ds")["y"])

    except Exception as e:
        st.error(f"Prophet model failed: {str(e)}")