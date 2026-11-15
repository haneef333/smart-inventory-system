# Smart Inventory & Demand Forecasting System

A recipe/BOM-driven inventory management platform with real-data-backed demand forecasting, built for small food businesses (bakeries, cafés, food stalls and similar).

This repo contains **two versions** of the same system:

| Version | Focus | Stack | Live Demo |
|---|---|---|---|
| **Full-stack web app** (`/fullstack`) | Software engineering: REST API, SPA frontend, deployment | React (Vite), FastAPI, SQLite, Recharts | [Frontend (Netlify)](https://bucolic-bombolone-5646dd.netlify.app) · [API docs (Render)](https://smart-inventory-system-m0we.onrender.com/docs) |
| **Streamlit app** (repo root) | Data science: forecasting and analytics | Python, Streamlit, Prophet, XGBoost, Plotly | [Streamlit demo](https://smart-inventory-system-ecm5houyjzh2vim7cbefyd.streamlit.app/) |

> **Note:** the backend runs on Render's free tier, so the first request after inactivity can take around a minute while the server wakes up.

---


## Problem Statement

Small food businesses often run out of key ingredients unexpectedly, or over-order and waste stock, because there is no simple way to:

1. Automatically deduct ingredient stock as orders come in, based on each product's recipe.
2. Get warned before an ingredient actually runs out.
3. Forecast future demand from real historical sales patterns instead of guesswork.

This project addresses all three in one system, backed by a relational SQLite schema and a properly evaluated forecasting pipeline.

---

## Features

- **Inventory management**: add, restock and delete ingredients, with configurable reorder thresholds and automatic low-stock alerts.
- **Recipe (BOM) management**: define ingredient requirements per product and view recipes per product or as a full list.
- **Order processing**: placing an order checks stock availability and deducts the correct ingredient quantities, logging revenue, cost and profit.
- **Analytics dashboard**: revenue and profit trends (daily and monthly), top products, revenue distribution and a live low-stock overview.
- **Demand forecasting**: trained on real bakery transaction data (Kaggle), comparing a moving-average baseline against XGBoost and Prophet, using a train/test split and engineered features (day of week, lag values, rolling averages, weekend flags).
- **Expenses, shopping list and tasks** (full-stack version): track expenses by category, generate shopping lists from low-stock items, and manage to-dos.
- **Self-seeding**: a fresh deployment builds the schema, imports the real dataset, generates demo sales and seeds starter ingredients and recipes automatically.

---

## Architecture (full-stack version)

```
┌─────────────┐      HTTP/JSON      ┌──────────────┐
│  React SPA  │ ──────────────────► │   FastAPI    │
│  (Netlify)  │ ◄────────────────── │   (Render)   │
└─────────────┘                     └──────┬───────┘
                                           │
                                           ▼
                                  SQLite (self-seeded)
                                           │
                              ┌────────────┴────────────┐
                              ▼                         ▼
                       Inventory / Orders        Forecast pipeline
                       Recipes / Expenses        (XGBoost, Moving Avg,
                                                  Prophet optional)
```

The API is documented automatically with Swagger at `/docs`.

---

## Model Evaluation

Forecast accuracy is evaluated per product on a held-out 30-day test split. Example (Bread):

| Model | RMSE | SMAPE (%) |
|---|---|---|
| Moving Average | 8.08 | _update_ |
| Prophet | 4.69 | _update_ |
| XGBoost | 6.03 | _update_ |

Prophet performed best on RMSE (4.69), roughly 42% lower error than the moving-average baseline. SMAPE replaced MAPE so that low-volume products do not cause divide-by-zero or inflated percentages.

---

## Tech Stack

**Full-stack version:** React, Vite, React Router, Recharts, Axios, FastAPI, SQLite, pandas, scikit-learn, XGBoost, (optional) Prophet

**Streamlit version:** Python, Streamlit, SQLite, Prophet, XGBoost, scikit-learn, Plotly, Pandas

---

## Run Locally

### Full-stack version

See [`fullstack/README.md`](fullstack/README.md) for backend and frontend setup.

### Streamlit version

```bash
git clone https://github.com/haneef333/smart-inventory-system.git
cd smart-inventory-system
pip install -r requirements.txt
streamlit run app.py
```

On first run the app builds the database, imports the historical dataset and seeds starter data, so no manual setup is needed.

---

## Project Structure

```
smart-inventory-system/
├── fullstack/
│   ├── backend/      # FastAPI REST API
│   └── frontend/     # React (Vite) SPA
├── app.py            # Streamlit entry point
├── ml_forecast.py    # Forecasting pipeline
├── data/             # Runtime data
└── BreadBasket_DMS.csv
```

---

## Author

**Mohammed Haneef** · [GitHub](https://github.com/haneef333)
