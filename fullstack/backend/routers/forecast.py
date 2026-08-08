import numpy as np
import pandas as pd
from fastapi import APIRouter, HTTPException
from sklearn.metrics import mean_squared_error
from xgboost import XGBRegressor

from database import get_connection

router = APIRouter(prefix="/api/forecast", tags=["forecast"])

_prophet_model_cache = {}
_xgb_model_cache = {}


def smape(y_true, y_pred):
    y_true = np.array(y_true)
    y_pred = np.array(y_pred)
    denominator = (np.abs(y_true) + np.abs(y_pred)) / 2
    denominator = np.where(denominator == 0, 1, denominator)
    return float(np.mean(np.abs(y_true - y_pred) / denominator) * 100)


@router.get("/products")
def list_forecastable_products():
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT Item FROM daily_product_demand_clean ORDER BY Item"
    ).fetchall()
    conn.close()
    return [r["Item"] for r in rows]


@router.get("/{product_name}")
def forecast_product(product_name: str):
    conn = get_connection()
    daily_df = pd.read_sql_query(
        "SELECT * FROM daily_product_demand_clean WHERE Item = ?",
        conn,
        params=(product_name,),
    )
    conn.close()

    if daily_df.empty:
        raise HTTPException(status_code=404, detail="No demand data for this product.")

    daily_df["Date"] = pd.to_datetime(daily_df["Date"], errors="coerce")
    daily_df = daily_df.dropna(subset=["Date"])

    daily = daily_df.rename(columns={"Date": "ds", "quantity_sold": "y"})[["ds", "y"]]
    daily = daily.sort_values("ds")

    daily["day_of_week"] = daily["ds"].dt.dayofweek
    daily["is_weekend"] = (daily["day_of_week"] >= 5).astype(int)
    daily["lag_1"] = daily["y"].shift(1)
    daily["lag_7"] = daily["y"].shift(7)
    daily["rolling_avg_7"] = daily["y"].rolling(window=7).mean()
    daily = daily.dropna().reset_index(drop=True)

    if len(daily) < 40:
        raise HTTPException(
            status_code=422,
            detail="Need at least 40 days of history for this product to forecast.",
        )

    train = daily.iloc[:-30]
    test = daily.iloc[-30:]

    feature_columns = ["day_of_week", "is_weekend", "lag_1", "lag_7", "rolling_avg_7"]
    X_train, y_train = train[feature_columns], train["y"]
    X_test, y_test = test[feature_columns], test["y"]

    actual = test.reset_index(drop=True)
    last_actual = float(actual["y"].iloc[-1])

    # --- XGBoost ---
    xgb_model = XGBRegressor(
        n_estimators=100, learning_rate=0.1, max_depth=4, random_state=42
    )
    xgb_model.fit(X_train, y_train)
    xgb_predictions = xgb_model.predict(X_test)
    xgb_prediction = float(xgb_predictions[-1])
    xgb_rmse = float(np.sqrt(mean_squared_error(y_test, xgb_predictions)))
    xgb_mape = smape(y_test, xgb_predictions)

    # --- Moving average baseline ---
    moving_average_prediction = float(train["y"].tail(7).mean())
    moving_average_predictions = np.repeat(moving_average_prediction, len(actual))
    baseline_rmse = float(np.sqrt(mean_squared_error(actual["y"], moving_average_predictions)))
    baseline_mape = smape(actual["y"], moving_average_predictions)

    # --- Prophet (optional dependency, degrades gracefully) ---
    prophet_available = False
    prophet_prediction = None
    prophet_rmse = None
    prophet_mape = None
    forecast_points = []

    try:
        from prophet import Prophet

        model = Prophet()
        model.fit(train[["ds", "y"]])
        future = model.make_future_dataframe(periods=30)
        forecast = model.predict(future)

        forecast_test = forecast.tail(30)[["ds", "yhat"]].reset_index(drop=True)
        prophet_prediction = float(forecast_test["yhat"].iloc[-1])
        prophet_rmse = float(np.sqrt(mean_squared_error(actual["y"], forecast_test["yhat"])))
        prophet_mape = smape(actual["y"], forecast_test["yhat"])
        prophet_available = True

        plot_df = forecast[["ds", "yhat", "yhat_lower", "yhat_upper"]].tail(90).copy()
        plot_df["ds"] = plot_df["ds"].astype(str)
        forecast_points = plot_df.to_dict(orient="records")
    except Exception:
        prophet_available = False

    trend_reference = prophet_prediction if prophet_available else xgb_prediction
    trend = "increasing" if trend_reference > last_actual else "decreasing"

    models = [
        {"model": "Moving Average", "prediction": round(moving_average_prediction, 2),
         "rmse": round(baseline_rmse, 2), "smape": round(baseline_mape, 2)},
        {"model": "XGBoost", "prediction": round(xgb_prediction, 2),
         "rmse": round(xgb_rmse, 2), "smape": round(xgb_mape, 2)},
    ]
    if prophet_available:
        models.insert(1, {
            "model": "Prophet", "prediction": round(prophet_prediction, 2),
            "rmse": round(prophet_rmse, 2), "smape": round(prophet_mape, 2),
        })

    best_model = min(models, key=lambda m: m["rmse"])

    history = daily[["ds", "y"]].copy()
    history["ds"] = history["ds"].astype(str)

    feature_importance = [
        {"feature": f, "importance": float(imp)}
        for f, imp in sorted(
            zip(feature_columns, xgb_model.feature_importances_),
            key=lambda x: x[1],
            reverse=True,
        )
    ]

    return {
        "product": product_name,
        "last_actual": last_actual,
        "trend": trend,
        "train_days": len(train),
        "test_days": len(test),
        "models": models,
        "best_model": best_model["model"],
        "prophet_available": prophet_available,
        "prophet_forecast": forecast_points,
        "history": history.tail(120).to_dict(orient="records"),
        "feature_importance": feature_importance,
    }
