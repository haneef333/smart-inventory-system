import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from database import init_schema
from data_pipeline import run_startup_pipeline
from routers import inventory, recipes, orders, dashboard, forecast, expenses, shopping_list, tasks, portfolio

app = FastAPI(title="Smart Inventory System API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # dev only — tighten this before deploying publicly
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "data", "portfolio_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads/portfolio", StaticFiles(directory=UPLOAD_DIR), name="portfolio_uploads")


@app.on_event("startup")
def on_startup():
    init_schema()
    run_startup_pipeline()


@app.get("/api/health")
def health():
    return {"status": "ok"}


app.include_router(inventory.router)
app.include_router(recipes.router)
app.include_router(orders.router)
app.include_router(dashboard.router)
app.include_router(forecast.router)
app.include_router(expenses.router)
app.include_router(shopping_list.router)
app.include_router(tasks.router)
app.include_router(portfolio.router)
