# Smart Inventory & Sales Forecasting System

An AI-powered inventory management and business analytics platform built for a bakery-style business, combining real-time inventory tracking, order management, and machine learning-based demand forecasting in a single interactive dashboard.

## Overview

This project goes beyond a typical CRUD app — it integrates a **Prophet time-series forecasting model** directly into a live business tool, so demand predictions update dynamically as new sales data comes in. It's designed to simulate a real small-business use case: tracking inventory, managing recipes/ingredients, processing orders, and forecasting what to stock next.

## Features

- **🔐 Login System** — simple session-based authentication
- **📊 Dashboard** — business analytics and KPIs at a glance
- **📦 Inventory Management** — track stock levels, categories, units, and cost per item
- **🍰 Recipe Management** — map products to the ingredients/quantities required to make them
- **🧾 Order Processing** — record orders with pricing and timestamps
- **📈 ML-Powered Demand Forecasting** — uses Facebook Prophet to predict next-day product demand from historical sales data, with trend detection (increasing/decreasing) and visual forecast plots
- **🌓 Theme Toggle** — light/dark mode
- **🗄️ Persistent Storage** — SQLite database with five relational tables (inventory, recipes, orders, sales, ingredient usage)

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend/App | Streamlit |
| Database | SQLite |
| ML/Forecasting | Facebook Prophet |
| Data Processing | Pandas |
| Language | Python |

## How the Forecasting Works

The forecasting module (`ml_forecast.py`) pulls historical sales data per product from the SQLite database, aggregates it into daily demand counts, and fits a Prophet model to generate a next-day demand prediction. It compares the predicted value against the most recent actual demand to classify the trend as increasing or decreasing, then visualizes both the forecast and historical demand curve directly in the dashboard. This lets a business user see forward-looking demand estimates without needing any data science background — the model runs invisibly in the background of a normal business tool.

## Database Design

Five relational tables handle the full business logic:
- `inventory` — raw stock items, quantities, and costs
- `recipes` — links products to the ingredients/quantities needed to produce them
- `orders` — customer orders with pricing and timestamps
- `sales` — revenue, cost, and profit per sale (feeds the forecasting model)
- `ingredient_usage` — tracks ingredient consumption over time

## What I Learned

- Integrating a real ML model (Prophet) into a live, interactive application rather than a static notebook
- Designing a relational schema to support inventory, recipes, and sales as connected entities
- Building a multi-page Streamlit app with session-state-based routing and authentication
- Handling edge cases in time-series forecasting (e.g., insufficient historical data, missing dates)

## Future Improvements

- Replace demo login with proper authentication (hashed passwords, multi-user support)
- Add automated ingredient reorder alerts based on forecasted demand
- Extend forecasting to multi-day/weekly horizons with confidence intervals
- Deploy with a hosted database (e.g., PostgreSQL) for production use

## Run Locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

---
*Built as part of an end-to-end data science / ML portfolio project.*
