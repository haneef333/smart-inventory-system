from fastapi import APIRouter, HTTPException

from database import get_connection
from schemas import ExpenseCreate

router = APIRouter(prefix="/api/expenses", tags=["expenses"])

# Common categories a home baker/bakery studio would use. The frontend uses
# this list to populate the category dropdown, but the field accepts any
# free-text value too.
CATEGORIES = [
    "Raw Material",
    "Packaging",
    "Equipment & Tools",
    "Delivery & Logistics",
    "Marketing",
    "Utilities & Rent",
    "Other",
]


@router.get("/categories")
def list_categories():
    return CATEGORIES


@router.get("")
def list_expenses():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM expenses ORDER BY expense_date DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("", status_code=201)
def add_expense(expense: ExpenseCreate):
    if expense.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO expenses (description, category, amount)
        VALUES (?, ?, ?)
        """,
        (expense.description, expense.category, expense.amount),
    )
    conn.commit()
    new_id = cursor.lastrowid
    row = cursor.execute("SELECT * FROM expenses WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return dict(row)


@router.delete("/{expense_id}")
def delete_expense(expense_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    existing = cursor.execute(
        "SELECT id FROM expenses WHERE id = ?", (expense_id,)
    ).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Expense not found.")

    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return {"deleted": expense_id}
