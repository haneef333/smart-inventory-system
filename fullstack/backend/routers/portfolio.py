import os
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File, Form

from database import get_connection

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])

UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "data", "portfolio_uploads")
UPLOAD_DIR = os.path.abspath(UPLOAD_DIR)
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}
MAX_FILE_SIZE = 8 * 1024 * 1024  # 8MB


@router.get("")
def list_portfolio_items():
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM portfolio_items ORDER BY created_at DESC"
    ).fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.post("", status_code=201)
async def add_portfolio_item(title: str = Form(...), image: UploadFile = File(...)):
    if not title.strip():
        raise HTTPException(status_code=400, detail="Title is required.")

    ext = os.path.splitext(image.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="Unsupported image type. Use jpg, png, webp, or gif.",
        )

    contents = await image.read()
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="Image must be under 8MB.")

    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = os.path.join(UPLOAD_DIR, filename)
    with open(filepath, "wb") as f:
        f.write(contents)

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO portfolio_items (title, image_filename) VALUES (?, ?)",
        (title.strip(), filename),
    )
    conn.commit()
    new_id = cursor.lastrowid
    row = cursor.execute(
        "SELECT * FROM portfolio_items WHERE id = ?", (new_id,)
    ).fetchone()
    conn.close()
    return dict(row)


@router.delete("/{item_id}")
def delete_portfolio_item(item_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    row = cursor.execute(
        "SELECT * FROM portfolio_items WHERE id = ?", (item_id,)
    ).fetchone()
    if row is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Portfolio item not found.")

    filepath = os.path.join(UPLOAD_DIR, row["image_filename"])
    if os.path.exists(filepath):
        os.remove(filepath)

    cursor.execute("DELETE FROM portfolio_items WHERE id = ?", (item_id,))
    conn.commit()
    conn.close()
    return {"deleted": item_id}
