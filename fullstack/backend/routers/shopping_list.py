from collections import defaultdict

from fastapi import APIRouter

from database import get_connection
from schemas import ShoppingListRequest

router = APIRouter(prefix="/api/shopping-list", tags=["shopping-list"])


def _inventory_map(cursor):
    rows = cursor.execute("SELECT * FROM inventory").fetchall()
    return {r["item_name"]: dict(r) for r in rows}


@router.get("/low-stock")
def low_stock_checklist():
    """Items currently at or below their reorder threshold, with a suggested
    restock quantity (tops back up to 2x the threshold) and estimated cost."""
    conn = get_connection()
    cursor = conn.cursor()
    inventory = _inventory_map(cursor)
    conn.close()

    items = []
    for item in inventory.values():
        threshold = item["reorder_threshold"] or 0
        qty = item["quantity"] or 0
        if qty <= threshold:
            suggested_qty = max((threshold * 2) - qty, threshold, 1)
            items.append({
                "item_name": item["item_name"],
                "category": item["category"],
                "unit": item["unit"],
                "current_quantity": qty,
                "reorder_threshold": threshold,
                "suggested_purchase_qty": round(suggested_qty, 2),
                "estimated_cost": round(suggested_qty * (item["cost_per_unit"] or 0), 2),
            })

    items.sort(key=lambda x: x["category"] or "")
    total_cost = round(sum(i["estimated_cost"] for i in items), 2)
    return {"items": items, "total_estimated_cost": total_cost}


@router.post("/generate")
def generate_shopping_list(request: ShoppingListRequest):
    """Build a purchase checklist from a set of planned/upcoming orders
    (ingredients needed, minus what's already in stock), optionally merged
    with items that are already running low regardless of planned orders."""
    conn = get_connection()
    cursor = conn.cursor()
    inventory = _inventory_map(cursor)

    needed = defaultdict(float)
    unresolved_products = []

    for line in request.items:
        recipe_rows = cursor.execute(
            "SELECT ingredient_name, quantity_needed, unit FROM recipes WHERE product_name = ?",
            (line.product_name,),
        ).fetchall()

        if not recipe_rows:
            unresolved_products.append(line.product_name)
            continue

        for r in recipe_rows:
            needed[r["ingredient_name"]] += r["quantity_needed"] * line.quantity

    conn.close()

    to_buy = {}
    for ingredient, qty_needed in needed.items():
        inv_item = inventory.get(ingredient)
        available = inv_item["quantity"] if inv_item else 0
        shortfall = qty_needed - available

        if shortfall > 0:
            cost_per_unit = inv_item["cost_per_unit"] if inv_item else 0
            to_buy[ingredient] = {
                "item_name": ingredient,
                "category": inv_item["category"] if inv_item else "Uncategorized",
                "unit": inv_item["unit"] if inv_item else None,
                "needed_for_orders": round(qty_needed, 2),
                "currently_in_stock": round(available, 2),
                "purchase_qty": round(shortfall, 2),
                "estimated_cost": round(shortfall * cost_per_unit, 2),
                "reason": "planned orders",
            }

    if request.include_low_stock:
        low_stock = low_stock_checklist()["items"]
        for item in low_stock:
            name = item["item_name"]
            if name in to_buy:
                # already covered by order shortfall — bump up to whichever is larger
                to_buy[name]["purchase_qty"] = round(
                    max(to_buy[name]["purchase_qty"], item["suggested_purchase_qty"]), 2
                )
                to_buy[name]["estimated_cost"] = round(
                    max(to_buy[name]["estimated_cost"], item["estimated_cost"]), 2
                )
                to_buy[name]["reason"] = "planned orders + low stock"
            else:
                to_buy[name] = {
                    "item_name": name,
                    "category": item["category"],
                    "unit": item["unit"],
                    "needed_for_orders": 0,
                    "currently_in_stock": item["current_quantity"],
                    "purchase_qty": item["suggested_purchase_qty"],
                    "estimated_cost": item["estimated_cost"],
                    "reason": "low stock",
                }

    items = sorted(to_buy.values(), key=lambda x: (x["category"] or "", x["item_name"]))
    total_cost = round(sum(i["estimated_cost"] for i in items), 2)

    return {
        "items": items,
        "total_estimated_cost": total_cost,
        "unresolved_products": unresolved_products,
    }
