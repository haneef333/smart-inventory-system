from fastapi import APIRouter, HTTPException

from database import get_connection
from schemas import TaskCreate, TaskUpdate

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.get("")
def list_tasks(month: str | None = None, date: str | None = None):
    """List tasks. Filter by month ('YYYY-MM') for calendar dots, or by an
    exact date ('YYYY-MM-DD') for a single day's task list."""
    conn = get_connection()
    cursor = conn.cursor()

    if date:
        rows = cursor.execute(
            "SELECT * FROM tasks WHERE task_date = ? ORDER BY id", (date,)
        ).fetchall()
    elif month:
        rows = cursor.execute(
            "SELECT * FROM tasks WHERE task_date LIKE ? ORDER BY task_date, id",
            (f"{month}%",),
        ).fetchall()
    else:
        rows = cursor.execute("SELECT * FROM tasks ORDER BY task_date, id").fetchall()

    conn.close()
    return [dict(r) for r in rows]


@router.post("", status_code=201)
def add_task(task: TaskCreate):
    if not task.title.strip():
        raise HTTPException(status_code=400, detail="Task title is required.")

    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (task_date, title) VALUES (?, ?)",
        (task.task_date, task.title.strip()),
    )
    conn.commit()
    new_id = cursor.lastrowid
    row = cursor.execute("SELECT * FROM tasks WHERE id = ?", (new_id,)).fetchone()
    conn.close()
    return dict(row)


@router.patch("/{task_id}")
def update_task(task_id: int, update: TaskUpdate):
    conn = get_connection()
    cursor = conn.cursor()

    existing = cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found.")

    is_done = existing["is_done"] if update.is_done is None else int(update.is_done)
    title = update.title.strip() if update.title else existing["title"]

    cursor.execute(
        "UPDATE tasks SET is_done = ?, title = ? WHERE id = ?",
        (is_done, title, task_id),
    )
    conn.commit()
    row = cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,)).fetchone()
    conn.close()
    return dict(row)


@router.delete("/{task_id}")
def delete_task(task_id: int):
    conn = get_connection()
    cursor = conn.cursor()
    existing = cursor.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
    if existing is None:
        conn.close()
        raise HTTPException(status_code=404, detail="Task not found.")

    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return {"deleted": task_id}
