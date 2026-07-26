import streamlit as st
import sqlite3
import pandas as pd

from prophet import Prophet

# Database connection
conn = sqlite3.connect(
    "data/bakery.db",
    check_same_thread=False
)


def show_ml_forecast_page():

    st.header("Advanced Demand Forecasting (Prophet Model)")

    # --------------------------------
    # LOAD REAL DAILY DEMAND DATA
    # --------------------------------

    daily_df = pd.read_sql_query(
        "SELECT * FROM daily_product_demand_clean",
        conn
    )

    if daily_df.empty:
        st.warning("No demand data available.")
        return

    # Convert Date column
    daily_df["Date"] = pd.to_datetime(
        daily_df["Date"],
        errors="coerce"
    )

    daily_df = daily_df.dropna(subset=["Date"])

    # --------------------------------
    # PRODUCT SELECTION
    # --------------------------------

    products = sorted(
        daily_df["Item"].unique()
    )

    selected_product = st.selectbox(
        "Select Product",
        products
    )

    # --------------------------------
    # FILTER SELECTED PRODUCT
    # --------------------------------

    product_df = daily_df[
        daily_df["Item"] == selected_product
    ].copy()

    # Prophet requires columns named ds and y
    daily = product_df.rename(
        columns={
            "Date": "ds",
            "quantity_sold": "y"
        }
    )[["ds", "y"]]

    daily = daily.sort_values("ds")

    if len(daily) < 10:
        st.warning(
            "Need at least 10 days of data for forecasting."
        )
        return

    # --------------------------------
    # PROPHET MODEL
    # --------------------------------

    try:

        model = Prophet()

        model.fit(daily)

        future = model.make_future_dataframe(
            periods=1
        )

        forecast = model.predict(future)

        predicted = forecast["yhat"].iloc[-1]

        last_actual = daily["y"].iloc[-1]

        if predicted > last_actual:
            trend = "Increasing 📈"
        else:
            trend = "Decreasing 📉"

        # --------------------------------
        # RESULTS
        # --------------------------------

        st.subheader("Forecast Result")

        st.success(
            f"""
            Product: {selected_product}

            Predicted Demand (Tomorrow): {round(predicted, 2)}

            Trend: {trend}
            """
        )

        # --------------------------------
        # FORECAST PLOT
        # --------------------------------

        st.subheader("Forecast Visualization")

        fig = model.plot(forecast)

        st.pyplot(fig)

        # --------------------------------
        # HISTORICAL DATA
        # --------------------------------

        st.subheader("Historical Demand")

        st.line_chart(
            daily.set_index("ds")["y"]
        )

        # --------------------------------
        # SHOW RAW DATA
        # --------------------------------

        with st.expander("View Demand Data"):

            st.dataframe(daily)

    except Exception as e:

        st.error(
            f"Prophet model failed: {str(e)}"
        )