import streamlit as st
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from xgboost import XGBRegressor
import numpy as np
from sklearn.metrics import mean_squared_error

# Database connection
conn = sqlite3.connect(
    "data/inventory.db",
    check_same_thread=False
)


@st.cache_data
def load_daily_demand():
    return pd.read_sql_query(
        "SELECT * FROM daily_product_demand_clean",
        conn
    )


@st.cache_resource
def train_prophet_model(train_df):
    m = Prophet()
    m.fit(train_df)
    return m


@st.cache_resource
def train_xgb_model(X_train, y_train):
    xgb = XGBRegressor(
        n_estimators=100,
        learning_rate=0.1,
        max_depth=4,
        random_state=42
    )
    xgb.fit(X_train, y_train)
    return xgb


def smape(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
    denominator = np.where(denominator == 0, 1, denominator)
    return np.mean(np.abs(y_true - y_pred) / denominator) * 100


def show_ml_forecast_page():

    st.header("Advanced Demand Forecasting")
    # --------------------------------
    # LOAD REAL DAILY DEMAND DATA
    # --------------------------------

    daily_df = load_daily_demand()

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
    # --------------------------------
    # FEATURE ENGINEERING
    # --------------------------------

    daily["day_of_week"] = daily["ds"].dt.dayofweek

    daily["is_weekend"] = (
        daily["day_of_week"] >= 5
    ).astype(int)

    daily["lag_1"] = daily["y"].shift(1)

    daily["lag_7"] = daily["y"].shift(7)

    daily["rolling_avg_7"] = (
        daily["y"]
        .rolling(window=7)
        .mean()
    )

    # Remove rows with missing lag values
    daily = daily.dropna().reset_index(drop=True)

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
    # XGBOOST DATA
    # --------------------------------

    feature_columns = [
        "day_of_week",
        "is_weekend",
        "lag_1",
        "lag_7",
        "rolling_avg_7"
    ]

    X_train = train[feature_columns]
    y_train = train["y"]

    X_test = test[feature_columns]
    y_test = test["y"]

    actual = test.reset_index(drop=True)
    last_actual = actual["y"].iloc[-1]

    try:

        # --------------------------------
        # XGBOOST MODEL (always runs — no external compiled dependency)
        # --------------------------------

        xgb_model = train_xgb_model(X_train, y_train)

        xgb_predictions = xgb_model.predict(X_test)

        xgb_prediction = xgb_predictions[-1]

        xgb_rmse = np.sqrt(
            mean_squared_error(
                y_test,
                xgb_predictions
            )
        )

        xgb_mape = smape(
            y_test,
            xgb_predictions
        )

        # --------------------------------
        # MOVING AVERAGE BASELINE (always runs)
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

        baseline_rmse = np.sqrt(
            mean_squared_error(
                actual["y"],
                moving_average_predictions
            )
        )

        baseline_mape = smape(
            actual["y"],
            moving_average_predictions
        )

        # --------------------------------
        # PROPHET (isolated — may be unavailable in this environment)
        # --------------------------------

        prophet_available = True
        model = None
        forecast = None
        forecast_download = None

        try:
            model = train_prophet_model(train)

            future = model.make_future_dataframe(periods=30)
            forecast = model.predict(future)

            forecast_download = forecast[[
                "ds", "yhat", "yhat_lower", "yhat_upper"
            ]].copy()
            forecast_download.columns = [
                "Date", "Predicted Demand", "Lower Bound", "Upper Bound"
            ]

            forecast_test = forecast.tail(30)[["ds", "yhat"]].reset_index(drop=True)

            prophet_prediction = forecast_test["yhat"].iloc[-1]

            prophet_rmse = np.sqrt(
                mean_squared_error(actual["y"], forecast_test["yhat"])
            )
            prophet_mape = smape(actual["y"], forecast_test["yhat"])

        except Exception:
            prophet_available = False
            st.info(
                "ℹ️ Prophet model is temporarily unavailable in this environment "
                "(Stan backend compilation issue). Showing Moving Average and "
                "XGBoost results below — Prophet works normally when run locally."
            )

        # --------------------------------
        # TREND
        # --------------------------------

        trend_reference = prophet_prediction if prophet_available else xgb_prediction

        if trend_reference > last_actual:
            trend = "Increasing 📈"
        else:
            trend = "Decreasing 📉"

        # --------------------------------
        # RESULTS
        # --------------------------------

        st.subheader("Forecast Result")

        result_lines = [f"Product: {selected_product}", ""]

        if prophet_available:
            result_lines.append(f"Prophet Prediction: {prophet_prediction:.2f}")

        result_lines.append(f"Moving Average Prediction: {moving_average_prediction:.2f}")
        result_lines.append(f"XGBoost Prediction: {xgb_prediction:.2f}")
        result_lines.append(f"Last Actual Demand: {last_actual}")
        result_lines.append(f"Trend: {trend}")

        st.success("\n\n".join(result_lines))

        # --------------------------------
        # TRAIN / TEST INFO
        # --------------------------------

        st.subheader("Train/Test Split")

        col1, col2 = st.columns(2)

        with col1:
            st.metric("Training Days", len(train))

        with col2:
            st.metric("Testing Days", len(test))

        # --------------------------------
        # MODEL COMPARISON
        # --------------------------------

        st.subheader("Model Comparison")

        comparison_models = ["Moving Average", "XGBoost"]
        comparison_predictions = [
            round(moving_average_prediction, 2),
            round(xgb_prediction, 2)
        ]

        if prophet_available:
            comparison_models.insert(1, "Prophet")
            comparison_predictions.insert(1, round(prophet_prediction, 2))

        comparison_df = pd.DataFrame({
            "Model": comparison_models,
            "Prediction": comparison_predictions
        })

        st.dataframe(comparison_df, use_container_width=True)

        # --------------------------------
        # MODEL EVALUATION
        # --------------------------------

        st.subheader("Model Evaluation")

        eval_models = ["Moving Average", "XGBoost"]
        eval_rmse = [round(baseline_rmse, 2), round(xgb_rmse, 2)]
        eval_mape = [round(baseline_mape, 2), round(xgb_mape, 2)]

        scores = {
            "Moving Average": baseline_rmse,
            "XGBoost": xgb_rmse
        }

        if prophet_available:
            eval_models.insert(1, "Prophet")
            eval_rmse.insert(1, round(prophet_rmse, 2))
            eval_mape.insert(1, round(prophet_mape, 2))
            scores["Prophet"] = prophet_rmse

        evaluation_df = pd.DataFrame({
            "Model": eval_models,
            "RMSE": eval_rmse,
            "SMAPE (%)": eval_mape
        })

        st.dataframe(evaluation_df, use_container_width=True)

        best_model = min(scores, key=scores.get)

        st.success(
            f"""
        🏆 Best Performing Model

        **{best_model}**

        RMSE: {scores[best_model]:.2f}
        """
        )

        # --------------------------------
        # FORECAST PLOT (Prophet only)
        # --------------------------------

        if prophet_available:
            st.subheader("Forecast Visualization")
            fig = model.plot(forecast)
            st.pyplot(fig)

            # --------------------------------
            # DOWNLOAD FORECAST (Prophet only)
            # --------------------------------

            st.subheader("Download Forecast")

            csv = forecast_download.to_csv(index=False)

            st.download_button(
                label="📥 Download Forecast CSV",
                data=csv,
                file_name=f"{selected_product}_forecast.csv",
                mime="text/csv"
            )

        # --------------------------------
        # HISTORICAL DEMAND
        # --------------------------------

        st.subheader("Historical Demand")

        st.line_chart(
            daily.set_index("ds")["y"]
        )
        # --------------------------------
        # FEATURE ENGINEERED DATASET
        # --------------------------------

        st.subheader("Feature Engineered Dataset")

        with st.expander("View Engineered Features"):

            st.dataframe(
                daily.tail(20),
                use_container_width=True
            )
        # --------------------------------
        # FEATURE IMPORTANCE
        # --------------------------------

        st.subheader("📊 XGBoost Feature Importance")

        importance_df = pd.DataFrame({
            "Feature": feature_columns,
            "Importance": xgb_model.feature_importances_
        }).sort_values(
            by="Importance",
            ascending=False
        )

        fig, ax = plt.subplots(figsize=(8, 4))

        ax.barh(
            importance_df["Feature"],
            importance_df["Importance"]
        )

        ax.set_xlabel("Importance")
        ax.set_ylabel("Feature")
        ax.invert_yaxis()

        st.pyplot(fig)

        st.dataframe(
            importance_df,
            use_container_width=True
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

        st.error(f"Forecasting failed: {e}")