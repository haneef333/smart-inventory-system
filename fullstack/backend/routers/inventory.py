from fastapi import APIRouter, HTTPException

from database import get_connection
from schemas import InventoryItemCreate, InventoryRestock

router = APIRouter(prefix="/api/inventory", tags=["inventory"])


@router.get("")
def list_inventory():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM inventory ORDER BY item_name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("", status_code=201)
def add_item(item: InventoryItemCreate):
    conn = get_connection()
    cursor = conn.cursor()

    existing = cursor.execute(
        "SELECT id FROM inventory WHERE item_name = ?", (item.item_name,)
    ).fetchone()

    if existing:
        conn.close()
        raise HTTPException(
            status_code=409,
            detail="Item already exists. Use the restock endpoint instead.",
        )

    cursor.execute(
        """
        INSERT INTO inventory
        (item_name, category, quantity, unit, cost_per_unit, reorder_threshold)
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            item.item_name,
            item.category,
            item.quantity,
            item.unit,
            item.cost_per_unit,
            item.reorder_threshold,
        ),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, **item.model_dump()}


@router.patch("/{item_id}/restock")
def restock_item(item_id: int, payload: InventoryRestock):
    conn = get_connection()
    cursor = conn.cursor()

    row = cursor.execute(
        "SELECT * FROM inventory WHERE id = ?", (item_id,)
    ).fetchone()

    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found.")

    new_quantity = row["quantity"] + payload.add_quantity
    cursor.execute(
        "UPDATE inventory SET quantity = ? WHERE id = ?", (new_quantity, item_id)
    )
    conn.commit()
    conn.close()
    return {"id": item_id, "quantity": new_quantity}


@router.delete("/{item_id}")
def delete_item(item_id: int):
    conn = get_connection()
    cursor = conn.cursor()

    row = cursor.execute(
        "SELECT id FROM inventory WHERE id = ?", (item_id,)
    ).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Item not found.")

    cursor.execute("DELETE FROM inventory WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"deleted": item_id}
