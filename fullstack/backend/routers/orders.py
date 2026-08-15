from fastapi import APIRouter, HTTPException

from database import get_connection
from schemas import OrderCreate, OrderStatusUpdate

router = APIRouter(prefix="/api/orders", tags=["orders"])


@router.get("")
def list_orders():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM orders ORDER BY order_date DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("", status_code=201)
def place_order(order: OrderCreate):
    conn = get_connection()
    cursor = conn.cursor()

    ingredients = cursor.execute(
        "SELECT ingredient_name, quantity_needed FROM recipes WHERE product_name = ?",
        (order.product_name,),
    ).fetchall()

    if not ingredients:
        conn.close()
        raise HTTPException(
            status_code=400, detail=f"No recipe found for '{order.product_name}'."
        )

    # --- Check stock availability for every ingredient first ---
    shortages = []
    needed_map = {}

    for row in ingredients:
        ingredient = row["ingredient_name"]
        quantity_needed = row["quantity_needed"] * order.order_quantity
        needed_map[ingredient] = quantity_needed

        inv_row = cursor.execute(
            "SELECT quantity, cost_per_unit FROM inventory WHERE item_name = ?",
            (ingredient,),
        ).fetchone()

        if inv_row is None:
            shortages.append(f"{ingredient} does not exist in inventory.")
            continue

        if inv_row["quantity"] < quantity_needed:
            shortages.append(
                f"Not enough stock for {ingredient}. Available: {inv_row['quantity']}, needed: {quantity_needed}"
            )

    if shortages:
        conn.close()
        raise HTTPException(status_code=409, detail=shortages)

    # --- Deduct stock, log usage, compute cost ---
    total_cost = 0.0

    for ingredient, quantity_needed in needed_map.items():
        inv_row = cursor.execute(
            "SELECT quantity, cost_per_unit FROM inventory WHERE item_name = ?",
            (ingredient,),
        ).fetchone()

        new_quantity = inv_row["quantity"] - quantity_needed
        cursor.execute(
            "UPDATE inventory SET quantity = ? WHERE item_name = ?",
            (new_quantity, ingredient),
        )

        ingredient_cost = quantity_needed * inv_row["cost_per_unit"]
        total_cost += ingredient_cost

        cursor.execute(
            """
            INSERT INTO ingredient_usage (ingredient_name, quantity_used)
            VALUES (?, ?)
            """,
            (ingredient, quantity_needed),
        )

    revenue = order.selling_price * order.order_quantity
    profit = revenue - total_cost

    cursor.execute(
        """
        INSERT INTO orders (product_name, quantity, selling_price, customer_name, due_date)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            order.product_name,
            order.order_quantity,
            order.selling_price,
            order.customer_name,
            order.due_date,
        ),
    )

    cursor.execute(
        """
        INSERT INTO sales (product_name, revenue, cost, profit)
        VALUES (?, ?, ?, ?)
        """,
        (order.product_name, revenue, total_cost, profit),
    )

    conn.commit()
    conn.close()

    return {
        "product_name": order.product_name,
        "quantity": order.order_quantity,
        "total_cost": round(total_cost, 2),
        "revenue": round(revenue, 2),
        "profit": round(profit, 2),
    }


@router.patch("/{order_id}/status")
def update_order_status(order_id: int, update: OrderStatusUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    existing = cursor.execute(
        "SELECT * FROM orders WHERE id = ?", (order_id,)
    ).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Order not found.")

    delivery_status = update.delivery_status or existing["delivery_status"]
    payment_status = update.payment_status or existing["payment_status"]

    cursor.execute(
        "UPDATE orders SET delivery_status = ?, payment_status = ? WHERE id = ?",
        (delivery_status, payment_status, order_id),
    )
    conn.commit()
    conn.close()

    return {"id": order_id, "delivery_status": delivery_status, "payment_status": payment_status}
