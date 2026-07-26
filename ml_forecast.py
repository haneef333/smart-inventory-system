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

    # Convert date
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
    # FILTER PRODUCT
    # --------------------------------

    product_df = daily_df[
        daily_df["Item"] == selected_product
    ].copy()

    daily = product_df.rename(
        columns={
            "Date": "ds",
            "quantity_sold": "y"
        }
    )[["ds", "y"]]

    daily = daily.sort_values("ds")

    if len(daily) < 40:
        st.warning(
            "Need at least 40 days of data for train/test forecasting."
        )
        return

    # --------------------------------
    # TRAIN / TEST SPLIT
    # --------------------------------

    train = daily.iloc[:-30]
    test = daily.iloc[-30:]

    # --------------------------------
    # TRAIN PROPHET
    # --------------------------------

    try:

        model = Prophet()

        model.fit(train)

        future = model.make_future_dataframe(
            periods=30
        )

        forecast = model.predict(future)

        forecast_test = forecast.tail(30)

        predicted = forecast_test["yhat"].iloc[-1]

        last_actual = test["y"].iloc[-1]

        # --------------------------------
        # TREND
        # --------------------------------

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

            Predicted Demand (30th Test Day): {predicted:.2f}

            Last Actual Demand: {last_actual}

            Trend: {trend}
            """
        )

        # --------------------------------
        # DATASET INFORMATION
        # --------------------------------

        st.subheader("Train/Test Split")

        col1, col2 = st.columns(2)

        with col1:
            st.metric(
                "Training Days",
                len(train)
            )

        with col2:
            st.metric(
                "Testing Days",
                len(test)
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
        # TRAINING DATA
        # --------------------------------

        with st.expander("Training Data"):

            st.dataframe(train)

        # --------------------------------
        # TEST DATA
        # --------------------------------

        with st.expander("Testing Data"):

            st.dataframe(test)

    except Exception as e:

        st.error(
            f"Prophet model failed: {str(e)}"
        )