# Smart Inventory & Demand Forecasting: Full-Stack Version

A full-stack rebuild of the Streamlit prototype, with a REST API backend and a React single-page frontend.

**Live:** [Frontend (Netlify)](https://bucolic-bombolone-5646dd.netlify.app) · [API docs (Render)](https://smart-inventory-system-m0we.onrender.com/docs)

> The backend is on Render's free tier. The first request after inactivity can take around a minute to respond while the server wakes up.

- **`backend/`**: FastAPI REST API (Python), SQLite, the same data pipeline and forecasting logic as the original (XGBoost + Moving Average, Prophet optional).
- **`frontend/`**: React (Vite) SPA that talks to the API over HTTP, with charts built in Recharts.

---

## Features

- Inventory with reorder thresholds, restocking and low-stock alerts
- Recipe (BOM) management per product
- Order placement with automatic stock deduction and profit tracking
- Dashboard with revenue and profit trends and top products
- Per-product demand forecasting
- Expense tracking by category
- Shopping list generated from low-stock items
- Task management

---

## Architecture

```
┌─────────────┐      HTTP/JSON      ┌──────────────┐
│  React SPA  │ ──────────────────► │   FastAPI    │
│  (frontend) │ ◄────────────────── │   (backend)  │
└─────────────┘                     └──────┬───────┘
                                           │
                                           ▼
                                 SQLite (data/inventory.db)
                                 self-seeded on first run
```

### API overview

| Area | Endpoints |
|---|---|
| Inventory | `GET/POST /api/inventory`, `PATCH /api/inventory/{id}/restock`, `DELETE /api/inventory/{id}` |
| Recipes | `GET/POST /api/recipes`, `GET /api/recipes/products`, `GET /api/recipes/{product}` |
| Orders | `GET/POST /api/orders`, `PATCH /api/orders/{id}/status` |
| Dashboard | `GET /api/dashboard/meta`, `GET /api/dashboard/summary` |
| Forecast | `GET /api/forecast/products`, `GET /api/forecast/{product}` |
| Expenses | `GET/POST /api/expenses`, `GET /api/expenses/categories`, `DELETE /api/expenses/{id}` |
| Shopping list | `GET /api/shopping-list/low-stock`, `POST /api/shopping-list/generate` |
| Tasks | `GET/POST /api/tasks`, `PATCH/DELETE /api/tasks/{id}` |

Full interactive docs are available at `/docs` (Swagger).

---

## Run Locally

**Backend**

```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8010
```

On first run it creates the schema, imports the Kaggle bakery dataset, generates demo sales and seeds starter ingredients and recipes.

**Frontend**

```bash
cd frontend
npm install
npm run dev
```

Opens at `http://localhost:5173`. The dev server proxies `/api/*` to `http://localhost:8010` (see `vite.config.js`), so both must be running.

---

## Deployment

| Part | Platform | Notes |
|---|---|---|
| Frontend | Netlify | Built from `fullstack/frontend` |
| Backend | Render (Web Service) | Free tier; sleeps after inactivity |

SQLite data on Render's free tier is not persistent across restarts, so the database re-seeds itself on startup.

---

## Tech Stack

**Backend:** FastAPI, SQLite, pandas, XGBoost, scikit-learn, (optional) Prophet

**Frontend:** React, Vite, React Router, Recharts, Axios
