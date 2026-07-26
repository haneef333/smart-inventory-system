import streamlit as st
import sqlite3
import pandas as pd

from prophet import Prophet
import numpy as np
from sklearn.metrics import (
    mean_squared_error,
    mean_absolute_percentage_error
)

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
            "Need at least 40 days of data for forecasting."
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

        # --------------------------------
        # PREPARE TEST PREDICTIONS
        # --------------------------------

        forecast_test = forecast.tail(30).copy()

        forecast_test = forecast_test[
            ["ds", "yhat"]
        ].reset_index(drop=True)

        actual = test.reset_index(drop=True)

        prophet_prediction = forecast_test["yhat"].iloc[-1]

        last_actual = actual["y"].iloc[-1]

        # --------------------------------
        # MOVING AVERAGE BASELINE
        # --------------------------------

        moving_average_prediction = (
            train["y"]
            .tail(7)
            .mean()
        )

        moving_average_predictions = np.repeat(
            moving_average_prediction,
            len(actual)
        )

        # --------------------------------
        # MODEL EVALUATION
        # --------------------------------

        prophet_rmse = np.sqrt(
            mean_squared_error(
                actual["y"],
                forecast_test["yhat"]
            )
        )

        prophet_mape = (
            mean_absolute_percentage_error(
                actual["y"],
                forecast_test["yhat"]
            ) * 100
        )

        baseline_rmse = np.sqrt(
            mean_squared_error(
                actual["y"],
                moving_average_predictions
            )
        )

        baseline_mape = (
            mean_absolute_percentage_error(
                actual["y"],
                moving_average_predictions
            ) * 100
        )

        # --------------------------------
        # TREND
        # --------------------------------

        if prophet_prediction > last_actual:
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

            Prophet Prediction: {prophet_prediction:.2f}

            Moving Average Prediction: {moving_average_prediction:.2f}

            Last Actual Demand: {last_actual}

            Trend: {trend}
            """
        )

        # --------------------------------
        # TRAIN / TEST INFO
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
        # MODEL COMPARISON
        # --------------------------------

        st.subheader("Model Comparison")

        comparison_df = pd.DataFrame({
            "Model": [
                "Moving Average",
                "Prophet"
            ],
            "Prediction": [
                round(moving_average_prediction, 2),
                round(prophet_prediction, 2)
            ]
        })

        st.dataframe(
            comparison_df,
            use_container_width=True
        )

        # --------------------------------
        # MODEL EVALUATION
        # --------------------------------

        st.subheader("Model Evaluation")

        evaluation_df = pd.DataFrame({
            "Model": [
                "Moving Average",
                "Prophet"
            ],
            "RMSE": [
                round(baseline_rmse, 2),
                round(prophet_rmse, 2)
            ],
            "MAPE (%)": [
                round(baseline_mape, 2),
                round(prophet_mape, 2)
            ]
        })

        st.dataframe(
            evaluation_df,
            use_container_width=True
        )

        if prophet_rmse < baseline_rmse:
            st.success(
                "✅ Prophet performs better than the Moving Average baseline."
            )
        else:
            st.info(
                "ℹ️ Moving Average performs as well as or better than Prophet."
            )

        # --------------------------------
        # FORECAST PLOT
        # --------------------------------

        st.subheader("Forecast Visualization")

        fig = model.plot(forecast)

        st.pyplot(fig)

        # --------------------------------
        # HISTORICAL DEMAND
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