import hmac
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

import auth
from database import init_schema
from data_pipeline import run_startup_pipeline
from routers import inventory, recipes, orders, dashboard, forecast, expenses, shopping_list, tasks, portfolio, online_orders

app = FastAPI(title="Smart Inventory System API")

# ---- Owner login: every /api route needs a token, except the few below ----
PUBLIC_API_PATHS = {"/api/health", "/api/auth/status", "/api/auth/login"}
INTEGRATION_SECRET = os.getenv("INTEGRATION_SECRET", "dev-integration-secret")


@app.middleware("http")
async def require_owner_login(request: Request, call_next):
    path = request.url.path
    if (
        not auth.auth_enabled()
        or request.method == "OPTIONS"  # browser pre-flight checks carry no token
        or not path.startswith("/api/")
        or path in PUBLIC_API_PATHS
    ):
        return await call_next(request)
    # Calls from the storefront prove themselves with the shared secret instead
    secret = request.headers.get("x-integration-secret")
    if secret and hmac.compare_digest(secret, INTEGRATION_SECRET):
        return await call_next(request)
    if auth.verify_token(auth.token_from_header(request.headers.get("authorization"))):
        return await call_next(request)
    return JSONResponse({"detail": "Please log in."}, status_code=401)


# Added after the login check on purpose: the middleware added last runs first,
# so CORS headers are on every response, including "please log in" ones.
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


app.include_router(auth.router)
app.include_router(inventory.router)
app.include_router(recipes.router)
app.include_router(orders.router)
app.include_router(dashboard.router)
app.include_router(forecast.router)
app.include_router(expenses.router)
app.include_router(shopping_list.router)
app.include_router(tasks.router)
app.include_router(portfolio.router)
app.include_router(online_orders.router)
