# Smart Inventory & Demand Forecasting — Full Stack

Converted from the original single-file Streamlit prototype into a proper
full-stack app:

- **backend/** — FastAPI REST API (Python), SQLite, same data pipeline and
  ML forecasting logic (XGBoost + Moving Average, Prophet optional) as the
  original.
- **frontend/** — React (Vite) single-page app, talks to the API over HTTP,
  charts via Recharts.

## Architecture

```
┌─────────────┐        HTTP/JSON        ┌──────────────┐
│   React SPA  │  ───────────────────►  │   FastAPI     │
│  (frontend)  │  ◄───────────────────  │   (backend)   │
└─────────────┘                         └──────┬───────┘
                                                │
                                                ▼
                                          SQLite (data/inventory.db)
                                          self-seeded on first run
```

## Run it locally

**Backend:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8010
```
First run auto-creates the schema, imports the real Kaggle bakery dataset,
generates demo sales, and seeds starter ingredients/recipes — same
self-seeding behavior as the original app, just triggered on API startup.

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```
Opens on `http://localhost:5173`. The dev server proxies `/api/*` requests
to `http://localhost:8010` (see `vite.config.js`), so both must be running.

## Suggested commit sequence

If you want a clean, reviewable git history instead of one giant commit,
push in this order:

1. **Scaffold** — root README, `.gitignore` files, empty `backend/` and
   `frontend/` folders.
2. **Backend: data layer** — `database.py`, `data_pipeline.py`,
   `requirements.txt`, `BreadBasket_DMS.csv`.
3. **Backend: API layer** — `schemas.py`, `routers/`, `main.py`.
4. **Backend: verify** — run it locally, commit any fixes.
5. **Frontend: scaffold** — Vite init (`package.json`, `index.html`,
   `vite.config.js`, `src/main.jsx`), design tokens (`src/index.css`).
6. **Frontend: shared components** — `src/components/` (Sidebar, Panel,
   TicketCard, ui.js) and `src/api/client.js`.
7. **Frontend: pages** — `Dashboard.jsx`, `Inventory.jsx`, `Recipes.jsx`,
   `Orders.jsx`, `Forecast.jsx`, and `App.jsx` wiring routes.
8. **Polish** — this README, final testing notes.

## Tech Stack

Backend: FastAPI, SQLite, pandas, XGBoost, scikit-learn, (optional) Prophet.
Frontend: React, Vite, React Router, Recharts, Axios.
