# Smart Inventory & Demand Forecasting System

A configurable, recipe/BOM-driven inventory management platform with real-data-backed demand forecasting — built for any small business that sells recipe-based products (bakeries, cafés, food stalls, and similar), not just one specific use case.

## Problem Statement

Small food businesses often run out of key ingredients unexpectedly, or over-order and waste stock, because there's no simple way to:
1. Automatically deduct ingredient stock as orders come in, based on each product's recipe.
2. Get warned before an ingredient actually runs out.
3. Forecast future demand using real historical sales patterns rather than guesswork.

This project addresses all three in one Streamlit application, backed by a relational SQLite schema and a properly evaluated forecasting pipeline.

## Architecture

```
┌──────────────┐      ┌───────────────┐      ┌───────────────┐
│  Inventory   │◄────►│    Recipes    │◄────►│    Orders     │
│ (ingredients)│      │  (product BOM)│      │ (place order) │
└──────┬───────┘      └───────────────┘      └───────┬───────┘
       │                                              │
       │ low-stock alerts                             │ deducts stock,
       ▼                                              │ logs sales
┌──────────────┐                              ┌───────▼───────┐
│  Dashboard   │◄─────────────────────────────│     Sales     │
│ (KPIs, charts)│                              │  (history)    │
└──────────────┘                              └───────────────┘

┌────────────────────────────────────────────────────────────┐
│                     Forecast Pipeline                       │
│ Real bakery transactions (Kaggle CSV)                        │
│   → daily_product_demand → daily_product_demand_clean        │
│   → Moving Average baseline vs Prophet vs XGBoost            │
│   → RMSE / MAPE evaluation, feature-engineered inputs         │
│   → cached trained models, live forecast + charts             │
└────────────────────────────────────────────────────────────┘
```

## Features

- **Inventory management** — add/restock/delete ingredients with configurable reorder thresholds and automatic low-stock alerts.
- **Recipe (BOM) management** — define ingredient requirements per product; view recipes individually per product or as a full list.
- **Order processing** — placing an order automatically checks stock availability and deducts the correct ingredient quantities, logging revenue, cost, and profit.
- **Analytics dashboard** — revenue/profit trends (daily & monthly), top products, revenue distribution, executive summary, and a live low-stock overview.
- **Demand forecasting** — trained on real bakery transaction data (not synthetic), comparing a naive moving-average baseline against Prophet and XGBoost, with train/test split evaluation (RMSE, MAPE) and feature engineering (day-of-week, lag values, rolling averages, weekend flags).
- **Self-seeding on first run** — a fresh deployment automatically builds demo sales data, imports the real demand dataset, and seeds starter ingredients/recipes with zero manual setup.

## Model Evaluation

Forecast accuracy is evaluated per-product on a held-out 30-day test split. Example (Bread):

| Model           | RMSE | MAPE (%) |
|-----------------|------|----------|
| Moving Average  | 8.08 | 45.45    |
| Prophet         | 4.69 | 26.34    |
| XGBoost         | 6.03 | 30.98    |

**Best performing model: Prophet** (RMSE 4.69) — outperforming the naive moving-average baseline by roughly 42% on RMSE and 42% on MAPE for this product.

## Tech Stack

Python, Streamlit, SQLite, Prophet, XGBoost, scikit-learn, Plotly, Matplotlib, Pandas

## Setup

```bash
git clone https://github.com/haneef333/smart-inventory-system.git
cd smart-inventory-system
pip install -r requirements.txt
streamlit run app.py
```

On first run, the app automatically builds the database, imports demo and real historical data, and seeds starter inventory/recipes — no manual setup required.

## Live Demo

https://smart-inventory-system-ecm5houyjzh2vim7cbefyd.streamlit.app/
