from datetime import datetime, date
from typing import Optional

import pandas as pd
from fastapi import APIRouter, Query

from database import get_connection

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


def _load_sales_df(conn):
    df = pd.read_sql_query("SELECT * FROM sales", conn)
    if df.empty:
        return df
    df["sale_date"] = pd.to_datetime(df["sale_date"], errors="coerce")
    df["revenue"] = pd.to_numeric(df["revenue"], errors="coerce").fillna(0)
    df["profit"] = pd.to_numeric(df["profit"], errors="coerce").fillna(0)
    return df.dropna(subset=["sale_date"])


@router.get("/meta")
def dashboard_meta():
    """Min/max sale date and product list, for populating filter controls."""
    conn = get_connection()
    df = _load_sales_df(conn)
    conn.close()

    if df.empty:
        return {"min_date": None, "max_date": None, "products": []}

    return {
        "min_date": df["sale_date"].min().date().isoformat(),
        "max_date": df["sale_date"].max().date().isoformat(),
        "products": sorted(df["product_name"].unique().tolist()),
    }


@router.get("/summary")
def dashboard_summary(
    start_date: Optional[date] = Query(None),
    end_date: Optional[date] = Query(None),
    product: Optional[str] = Query(None),
):
    conn = get_connection()
    df = _load_sales_df(conn)
    inventory_df = pd.read_sql_query("SELECT * FROM inventory", conn)
    conn.close()

    if df.empty:
        return {"empty": True}

    if start_date:
        df = df[df["sale_date"].dt.date >= start_date]
    if end_date:
        df = df[df["sale_date"].dt.date <= end_date]
    if product and product != "All":
        df = df[df["product_name"] == product]

    if df.empty:
        return {"empty": True}

    total_orders = len(df)
    total_revenue = float(df["revenue"].sum())
    total_profit = float(df["profit"].sum())

    highest_revenue_product = df.groupby("product_name")["revenue"].sum().idxmax()
    highest_profit_product = df.groupby("product_name")["profit"].sum().idxmax()
    average_order_value = float(df["revenue"].mean())

    low_stock = inventory_df[
        inventory_df["quantity"] <= inventory_df["reorder_threshold"]
    ]

    daily_revenue = (
        df.groupby(df["sale_date"].dt.date)["revenue"].sum().reset_index()
    )
    daily_revenue.columns = ["date", "revenue"]
    daily_revenue["date"] = daily_revenue["date"].astype(str)

    daily_profit = (
        df.groupby(df["sale_date"].dt.date)["profit"].sum().reset_index()
    )
    daily_profit.columns = ["date", "profit"]
    daily_profit["date"] = daily_profit["date"].astype(str)

    monthly_revenue = (
        df.groupby(df["sale_date"].dt.to_period("M"))["revenue"].sum().reset_index()
    )
    monthly_revenue["sale_date"] = monthly_revenue["sale_date"].astype(str)
    monthly_revenue.columns = ["month", "revenue"]

    monthly_profit = (
        df.groupby(df["sale_date"].dt.to_period("M"))["profit"].sum().reset_index()
    )
    monthly_profit["sale_date"] = monthly_profit["sale_date"].astype(str)
    monthly_profit.columns = ["month", "profit"]

    top_products = df["product_name"].value_counts().reset_index()
    top_products.columns = ["product", "orders"]

    product_revenue = (
        df.groupby("product_name")["revenue"].sum().reset_index()
    )
    product_revenue.columns = ["product", "revenue"]

    recent_sales = (
        df.sort_values(by="sale_date", ascending=False)
        .head(10)
        .copy()
    )
    recent_sales["sale_date"] = recent_sales["sale_date"].astype(str)

    return {
        "empty": False,
        "kpis": {
            "total_orders": total_orders,
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
        },
        "executive_summary": {
            "highest_revenue_product": highest_revenue_product,
            "highest_profit_product": highest_profit_product,
            "average_order_value": round(average_order_value, 2),
            "total_products": int(inventory_df["item_name"].nunique()),
        },
        "inventory_overview": {
            "products_in_inventory": len(inventory_df),
            "total_stock": float(inventory_df["quantity"].sum()),
            "low_stock_count": len(low_stock),
            "low_stock_items": low_stock[
                ["item_name", "quantity", "reorder_threshold"]
            ].to_dict(orient="records"),
        },
        "charts": {
            "daily_revenue": daily_revenue.to_dict(orient="records"),
            "daily_profit": daily_profit.to_dict(orient="records"),
            "monthly_revenue": monthly_revenue.to_dict(orient="records"),
            "monthly_profit": monthly_profit.to_dict(orient="records"),
            "top_products": top_products.to_dict(orient="records"),
            "product_revenue": product_revenue.to_dict(orient="records"),
        },
        "recent_sales": recent_sales.to_dict(orient="records"),
    }
