from fastapi import APIRouter

from database import get_connection
from schemas import RecipeCreate

router = APIRouter(prefix="/api/recipes", tags=["recipes"])


@router.get("")
def list_recipes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM recipes ORDER BY product_name").fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/products")
def list_products():
    """Distinct product names that have at least one recipe defined."""
    conn = get_connection()
    rows = conn.execute(
        "SELECT DISTINCT product_name FROM recipes ORDER BY product_name"
    ).fetchall()
    conn.close()
    return [r["product_name"] for r in rows]


@router.get("/{product_name}")
def get_recipe(product_name: str):
    conn = get_connection()
    rows = conn.execute(
        "SELECT ingredient_name, quantity_needed, unit FROM recipes WHERE product_name = ?",
        (product_name,),
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("", status_code=201)
def add_recipe_line(recipe: RecipeCreate):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO recipes (product_name, ingredient_name, quantity_needed, unit)
        VALUES (?, ?, ?, ?)
        """,
        (recipe.product_name, recipe.ingredient_name, recipe.quantity_needed, recipe.unit),
    )
    conn.commit()
    new_id = cursor.lastrowid
    conn.close()
    return {"id": new_id, **recipe.model_dump()}
