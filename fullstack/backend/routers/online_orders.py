"""
Online orders: orders placed by customers on the storefront (MERN) app.

Flow
  1. Storefront  -> POST /api/online-orders            order arrives with status "new"
  2. Owner       -> POST /api/online-orders/{id}/accept stock is checked and deducted
                                                        using the recipes table
     or          -> POST /api/online-orders/{id}/decline
  3. Owner       -> PATCH /api/online-orders/{id}/status baking -> ready -> completed
  4. After every change this app calls the storefront back so the customer
     sees the new status. Failed callbacks are retried automatically.

Calls from the storefront must carry the shared secret in the
`x-integration-secret` header (env var INTEGRATION_SECRET, same value in both apps).
"""

import hmac
import json
import math
import os
import urllib.error
import urllib.request
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, Header, HTTPException, Response, WebSocket, WebSocketDisconnect

from auth import auth_enabled, verify_token
from database import get_connection
from realtime import hub, notify_owner
from schemas import OnlineOrderDecline, OnlineOrderIn, OnlineOrderStatusUpdate

DEV_SECRET = "dev-integration-secret"
INTEGRATION_SECRET = os.getenv("INTEGRATION_SECRET", DEV_SECRET)
STOREFRONT_API_URL = os.getenv("STOREFRONT_API_URL", "http://127.0.0.1:5000").rstrip("/")

if INTEGRATION_SECRET == DEV_SECRET:
    print("[online-orders] INTEGRATION_SECRET is the development default. Set it before deploying.")

router = APIRouter(prefix="/api/online-orders", tags=["online orders"])

ACTIVE_STATUSES = ("accepted", "baking", "ready")
DONE_STATUSES = ("completed", "declined", "cancelled")
NEXT_STATUS = {"accepted": ("baking", "ready", "completed"), "baking": ("ready", "completed"), "ready": ("completed",)}


# ---------------------------------------------------------------- helpers

def require_storefront(x_integration_secret: Optional[str] = Header(default=None)):
    if not x_integration_secret or not hmac.compare_digest(x_integration_secret, INTEGRATION_SECRET):
        raise HTTPException(status_code=401, detail="Invalid integration secret.")


def _load_order(conn, order_id):
    row = conn.execute("SELECT * FROM online_orders WHERE id = ?", (order_id,)).fetchone()
    if row is None:
        return None
    order = dict(row)
    order["items"] = [
        dict(r)
        for r in conn.execute(
            "SELECT product_name, display_name, quantity, unit_price, recipe_scale, details, photo_url "
            "FROM online_order_items WHERE online_order_id = ? ORDER BY id",
            (order_id,),
        ).fetchall()
    ]
    return order


def _ingredient_needs(cursor, items):
    """Total quantity of each ingredient needed for all items in an order.
    recipe_scale covers sizes: a 2 kg cake uses twice the 1 kg recipe."""
    needs, missing_recipes = {}, []
    for item in items:
        rows = cursor.execute(
            "SELECT ingredient_name, quantity_needed FROM recipes WHERE product_name = ?",
            (item["product_name"],),
        ).fetchall()
        if not rows:
            missing_recipes.append(item["product_name"])
            continue
        for r in rows:
            scale = item.get("recipe_scale") or 1
            needs[r["ingredient_name"]] = needs.get(r["ingredient_name"], 0) + r["quantity_needed"] * item["quantity"] * scale
    return needs, missing_recipes


def _stock_check(cursor, items):
    needs, missing_recipes = _ingredient_needs(cursor, items)
    shortages = [f"No recipe found for '{name}'. Add it on the Recipes page." for name in missing_recipes]
    for ingredient, quantity_needed in needs.items():
        inv = cursor.execute(
            "SELECT quantity, unit FROM inventory WHERE item_name = ?", (ingredient,)
        ).fetchone()
        if inv is None:
            shortages.append(f"{ingredient} does not exist in inventory.")
        elif inv["quantity"] < quantity_needed:
            unit = inv["unit"] or ""
            shortages.append(
                f"Not enough {ingredient}: need {quantity_needed:g} {unit}, have {inv['quantity']:g} {unit}.".replace("  ", " ")
            )
    return needs, shortages


def _notify_storefront(order_id):
    """Tell the storefront about this order's current status. Runs in the background."""
    conn = get_connection()
    try:
        order = conn.execute("SELECT * FROM online_orders WHERE id = ?", (order_id,)).fetchone()
        if order is None or order["status"] in ("new", "cancelled"):
            return

        body = json.dumps({
            "external_id": order["external_id"],
            "status": order["status"],
            "note": order["status_note"] or "",
            "payment_status": order["payment_status"],
        }).encode()
        req = urllib.request.Request(
            f"{STOREFRONT_API_URL}/api/integrations/inventory/order-status",
            data=body,
            method="POST",
            headers={"content-type": "application/json", "x-integration-secret": INTEGRATION_SECRET},
        )

        state, error = "sent", None
        try:
            with urllib.request.urlopen(req, timeout=15) as res:
                res.read()
        except urllib.error.HTTPError as e:
            # 4xx means the storefront understood us but refused: retrying will not help
            state = "rejected" if 400 <= e.code < 500 else "failed"
            error = f"Storefront replied {e.code}: {e.read().decode(errors='ignore')[:300]}"
        except Exception as e:  # network error, timeout, storefront asleep
            state, error = "failed", f"Could not reach storefront: {e}"

        conn.execute(
            "UPDATE online_orders SET callback_state = ?, callback_error = ?, "
            "callback_attempts = callback_attempts + 1, callback_at = CURRENT_TIMESTAMP WHERE id = ?",
            (state, error, order_id),
        )
        conn.commit()
        if error:
            print(f"[online-orders] callback for {order['external_id']} {state}: {error}")
    finally:
        conn.close()


def _retry_failed_callbacks():
    conn = get_connection()
    ids = [
        r["id"]
        for r in conn.execute(
            "SELECT id FROM online_orders WHERE callback_state IN ('pending', 'failed') "
            "AND callback_attempts < 30 "
            "AND (callback_at IS NULL OR callback_at < datetime('now', '-30 seconds')) "
            "LIMIT 10"
        ).fetchall()
    ]
    conn.close()
    for order_id in ids:
        _notify_storefront(order_id)


def _mark_changed(cursor, order_id, **fields):
    fields["callback_state"] = "pending"
    sets = ", ".join(f"{k} = ?" for k in fields)
    cursor.execute(
        f"UPDATE online_orders SET {sets}, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
        (*fields.values(), order_id),
    )


# ---------------------------------------------------------------- storefront -> inventory

@router.post("", status_code=201, dependencies=[Depends(require_storefront)])
def receive_order(order: OnlineOrderIn, response: Response):
    conn = get_connection()
    cursor = conn.cursor()

    existing = cursor.execute(
        "SELECT id FROM online_orders WHERE external_id = ?", (order.external_id,)
    ).fetchone()
    if existing:  # the storefront retried; we already have it
        result = _load_order(conn, existing["id"])
        conn.close()
        response.status_code = 200
        return result

    cursor.execute(
        """
        INSERT INTO online_orders
        (external_id, customer_name, customer_phone, customer_email, fulfilment, address,
         due_date, time_slot, payment_method, notes, delivery_fee, coupon_code, discount, total)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            order.external_id, order.customer_name, order.customer_phone, order.customer_email,
            order.fulfilment, order.address, order.due_date, order.time_slot, order.payment_method,
            order.notes, order.delivery_fee, order.coupon_code, order.discount, order.total,
        ),
    )
    order_id = cursor.lastrowid
    cursor.executemany(
        "INSERT INTO online_order_items "
        "(online_order_id, product_name, display_name, quantity, unit_price, recipe_scale, details, photo_url) "
        "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
        [
            (order_id, i.product_name, i.display_name, i.quantity, i.unit_price, i.recipe_scale, i.details, i.photo_url)
            for i in order.items
        ],
    )
    conn.commit()
    result = _load_order(conn, order_id)
    conn.close()
    notify_owner("new_order", id=order_id, external_id=order.external_id, customer=order.customer_name, total=order.total)
    return result


@router.post("/by-external/{external_id}/cancel", dependencies=[Depends(require_storefront)])
def cancel_by_customer(external_id: str):
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT id, status FROM online_orders WHERE external_id = ?", (external_id,)
    ).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found.")
    if row["status"] == "cancelled":
        conn.close()
        return {"id": row["id"], "status": "cancelled"}

    cursor.execute(
        "UPDATE online_orders SET status = 'cancelled', status_note = 'Cancelled by customer', "
        "updated_at = CURRENT_TIMESTAMP WHERE id = ? AND status = 'new'",
        (row["id"],),
    )
    if cursor.rowcount == 0:
        conn.close()
        raise HTTPException(status_code=409, detail=f"Order is already {row['status']}.")
    conn.commit()
    conn.close()
    notify_owner("order_changed", id=row["id"], status="cancelled")
    return {"id": row["id"], "status": "cancelled"}


@router.get("/availability", dependencies=[Depends(require_storefront)])
def availability():
    """How many of each product can be made with the stock on hand right now."""
    conn = get_connection()
    stock = {
        r["item_name"]: r["quantity"] or 0
        for r in conn.execute("SELECT item_name, quantity FROM inventory").fetchall()
    }
    recipes = {}
    for r in conn.execute("SELECT product_name, ingredient_name, quantity_needed FROM recipes").fetchall():
        recipes.setdefault(r["product_name"], []).append((r["ingredient_name"], r["quantity_needed"]))
    conn.close()

    result = {}
    for product, lines in recipes.items():
        can_make = 999
        for ingredient, needed in lines:
            if not needed or needed <= 0:
                continue
            can_make = min(can_make, math.floor(stock.get(ingredient, 0) / needed))
        result[product] = max(can_make, 0)
    return result


# ---------------------------------------------------------------- owner (inventory UI)

@router.get("")
def list_online_orders(background_tasks: BackgroundTasks, status: str = "all"):
    """status: new | active | done | all"""
    conn = get_connection()
    cursor = conn.cursor()

    query, params = "SELECT id FROM online_orders", ()
    if status == "new":
        query += " WHERE status = 'new'"
    elif status == "active":
        query += f" WHERE status IN {ACTIVE_STATUSES}"
    elif status == "done":
        query += f" WHERE status IN {DONE_STATUSES}"
    query += " ORDER BY CASE status WHEN 'new' THEN 0 ELSE 1 END, due_date ASC, id DESC LIMIT 200"

    orders = []
    for r in cursor.execute(query, params).fetchall():
        order = _load_order(conn, r["id"])
        if order["status"] == "new":
            _, shortages = _stock_check(cursor, order["items"])
            order["stock_check"] = {"can_fulfil": not shortages, "shortages": shortages}
        orders.append(order)
    conn.close()

    # The owner's page polls this endpoint, which doubles as a retry loop
    background_tasks.add_task(_retry_failed_callbacks)
    return orders


@router.get("/summary")
def online_orders_summary():
    conn = get_connection()
    row = conn.execute(
        f"""
        SELECT
          SUM(CASE WHEN status = 'new' THEN 1 ELSE 0 END) AS new,
          SUM(CASE WHEN status IN {ACTIVE_STATUSES} THEN 1 ELSE 0 END) AS active
        FROM online_orders
        """
    ).fetchone()
    conn.close()
    return {"new": row["new"] or 0, "active": row["active"] or 0}


@router.post("/{order_id}/accept")
def accept_order(order_id: int, background_tasks: BackgroundTasks):
    conn = get_connection()
    cursor = conn.cursor()
    order = _load_order(conn, order_id)
    if order is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found.")

    # Claim the order first so a double click cannot deduct stock twice
    cursor.execute(
        "UPDATE online_orders SET status = 'accepted', decided_at = CURRENT_TIMESTAMP "
        "WHERE id = ? AND status = 'new'",
        (order_id,),
    )
    if cursor.rowcount == 0:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=409, detail=[f"This order is already {order['status']}."])

    needs, shortages = _stock_check(cursor, order["items"])
    if shortages:
        conn.rollback()
        conn.close()
        raise HTTPException(status_code=409, detail=shortages)

    # --- Deduct stock and log usage (same as placing an order on the Orders page) ---
    cost_per_unit = {}
    for ingredient, quantity_needed in needs.items():
        inv = cursor.execute(
            "SELECT quantity, cost_per_unit FROM inventory WHERE item_name = ?", (ingredient,)
        ).fetchone()
        cost_per_unit[ingredient] = inv["cost_per_unit"] or 0
        cursor.execute(
            "UPDATE inventory SET quantity = ? WHERE item_name = ?",
            (inv["quantity"] - quantity_needed, ingredient),
        )
        cursor.execute(
            "INSERT INTO ingredient_usage (ingredient_name, quantity_used) VALUES (?, ?)",
            (ingredient, quantity_needed),
        )

    # --- One orders + sales row per item, so the dashboard and forecasts include online sales ---
    # A coupon discount is shared across the items in proportion to their price
    items_total = sum(i["unit_price"] * i["quantity"] for i in order["items"]) or 1
    revenue_share = max(items_total - (order.get("discount") or 0), 0) / items_total
    total_revenue = total_cost = 0.0
    for item in order["items"]:
        recipe = cursor.execute(
            "SELECT ingredient_name, quantity_needed FROM recipes WHERE product_name = ?",
            (item["product_name"],),
        ).fetchall()
        scale = item.get("recipe_scale") or 1
        item_cost = sum(r["quantity_needed"] * item["quantity"] * scale * cost_per_unit.get(r["ingredient_name"], 0) for r in recipe)
        revenue = item["unit_price"] * item["quantity"] * revenue_share
        total_revenue += revenue
        total_cost += item_cost

        cursor.execute(
            """
            INSERT INTO orders (product_name, quantity, selling_price, customer_name, due_date,
                                payment_method, payment_status, online_order_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                item["product_name"], item["quantity"], item["unit_price"], order["customer_name"],
                order["due_date"], order["payment_method"], order["payment_status"], order_id,
            ),
        )
        cursor.execute(
            "INSERT INTO sales (product_name, revenue, cost, profit) VALUES (?, ?, ?, ?)",
            (item["product_name"], revenue, item_cost, revenue - item_cost),
        )

    _mark_changed(cursor, order_id, status_note="")
    conn.commit()
    result = _load_order(conn, order_id)
    conn.close()

    background_tasks.add_task(_notify_storefront, order_id)
    notify_owner("order_changed", id=order_id, status="accepted")
    return {
        "order": result,
        "revenue": round(total_revenue, 2),
        "total_cost": round(total_cost, 2),
        "profit": round(total_revenue - total_cost, 2),
        "deducted": {k: round(v, 2) for k, v in needs.items()},
    }


@router.post("/{order_id}/decline")
def decline_order(order_id: int, payload: OnlineOrderDecline, background_tasks: BackgroundTasks):
    conn = get_connection()
    cursor = conn.cursor()
    reason = (payload.reason or "").strip() or "The baker could not take this order."
    cursor.execute(
        "UPDATE online_orders SET status = 'declined', decided_at = CURRENT_TIMESTAMP "
        "WHERE id = ? AND status = 'new'",
        (order_id,),
    )
    if cursor.rowcount == 0:
        row = cursor.execute("SELECT status FROM online_orders WHERE id = ?", (order_id,)).fetchone()
        conn.close()
        if row is None:
            raise HTTPException(status_code=404, detail="Order not found.")
        raise HTTPException(status_code=409, detail=f"This order is already {row['status']}.")

    _mark_changed(cursor, order_id, status_note=reason[:300])
    conn.commit()
    result = _load_order(conn, order_id)
    conn.close()
    background_tasks.add_task(_notify_storefront, order_id)
    notify_owner("order_changed", id=order_id, status="declined")
    return result


@router.patch("/{order_id}/status")
def update_online_order_status(order_id: int, update: OnlineOrderStatusUpdate, background_tasks: BackgroundTasks):
    conn = get_connection()
    cursor = conn.cursor()
    order = cursor.execute("SELECT status FROM online_orders WHERE id = ?", (order_id,)).fetchone()
    if order is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found.")

    fields = {}
    if update.status and update.status != order["status"]:
        if update.status not in NEXT_STATUS.get(order["status"], ()):
            conn.close()
            raise HTTPException(status_code=409, detail=f"Cannot move an order from {order['status']} to {update.status}.")
        fields["status"] = update.status
        fields["status_note"] = ""
        if update.status == "completed":
            cursor.execute(
                "UPDATE orders SET delivery_status = 'delivered' WHERE online_order_id = ?", (order_id,)
            )

    if update.payment_status:
        fields["payment_status"] = update.payment_status
        cursor.execute(
            "UPDATE orders SET payment_status = ? WHERE online_order_id = ?", (update.payment_status, order_id)
        )

    if fields:
        _mark_changed(cursor, order_id, **fields)
        conn.commit()
        background_tasks.add_task(_notify_storefront, order_id)
        notify_owner("order_changed", id=order_id, status=fields.get("status"))

    result = _load_order(conn, order_id)
    conn.close()
    return result


# ---------------------------------------------------------------- live alerts for the owner

@router.websocket("/ws")
async def owner_alerts(ws: WebSocket, token: str | None = None):
    """The owner's app connects here to hear about new orders instantly."""
    if auth_enabled() and not verify_token(token):
        await ws.close(code=4401)  # 4401 = not logged in
        return
    await hub.connect(ws)
    try:
        while True:
            await ws.receive_text()  # the browser sends a ping now and then
    except WebSocketDisconnect:
        pass
    finally:
        hub.disconnect(ws)
