from fastapi import FastAPI, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import sqlite3

# Import Auth Router
from app.auth import router as auth_router

app = FastAPI(
    title="Task Management API with Authentication",
    description="""
A RESTful CRUD API with Supabase Authentication.

### Features
- User Signup
- User Login
- Protected Routes
- Create Tasks
- Read Tasks
- Update Tasks
- Delete Tasks
""",
    version="2.0.0",
)

# Register Authentication Routes
app.include_router(
    auth_router,
    prefix="/auth",
    tags=["Authentication"]
)

# =====================================================
# Pydantic Models
# =====================================================

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str
    done: bool


# =====================================================
# SQLite Database
# =====================================================

DB_NAME = "tasks.db"


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done INTEGER NOT NULL DEFAULT 0
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    count = cursor.fetchone()[0]

    if count == 0:
        seed_tasks = [
            ("Learn FastAPI", 0),
            ("Build CRUD API", 0),
            ("Push to GitHub", 1)
        ]

        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            seed_tasks
        )

    conn.commit()
    conn.close()


init_db()


# =====================================================
# Root Endpoint
# =====================================================

@app.get("/", summary="API Information")
def root():
    return {
        "name": "Task API",
        "version": "2.0",
        "features": [
            "Authentication",
            "CRUD Tasks"
        ]
    }


# =====================================================
# Health Check
# =====================================================

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# =====================================================
# Public Route
# =====================================================

@app.get("/public/info")
def public_info():
    return {
        "message": "Welcome stranger! This info is public."
    }


# =====================================================
# Get All Tasks
# =====================================================

@app.get("/tasks")
def get_tasks():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM tasks")
    rows = cursor.fetchall()

    conn.close()

    return [dict(row) for row in rows]


# =====================================================
# Get Task By ID
# =====================================================

@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id=?",
        (task_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    return dict(row)


# =====================================================
# Create Task
# =====================================================

@app.post("/tasks", status_code=201)
def create_task(task: TaskCreate):

    if not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "INSERT INTO tasks(title,done) VALUES (?,?)",
        (task.title, 0)
    )

    task_id = cursor.lastrowid

    conn.commit()

    cursor.execute(
        "SELECT * FROM tasks WHERE id=?",
        (task_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return dict(row)


# =====================================================
# Update Task
# =====================================================

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task: TaskUpdate):

    if not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required"}
        )

    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    cursor.execute(
        "SELECT * FROM tasks WHERE id=?",
        (task_id,)
    )

    if cursor.fetchone() is None:
        conn.close()

        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    cursor.execute(
        """
        UPDATE tasks
        SET title=?, done=?
        WHERE id=?
        """,
        (
            task.title,
            int(task.done),
            task_id
        )
    )

    conn.commit()

    cursor.execute(
        "SELECT * FROM tasks WHERE id=?",
        (task_id,)
    )

    row = cursor.fetchone()

    conn.close()

    return dict(row)


# =====================================================
# Delete Task
# =====================================================

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    cursor.execute(
        "SELECT id FROM tasks WHERE id=?",
        (task_id,)
    )

    if cursor.fetchone() is None:

        conn.close()

        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    cursor.execute(
        "DELETE FROM tasks WHERE id=?",
        (task_id,)
    )

    conn.commit()

    conn.close()

    return Response(status_code=204)