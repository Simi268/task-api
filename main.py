from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()


# ----------------------------
# Pydantic Models
# ----------------------------

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str
    done: bool


# ----------------------------
# In-Memory Database
# ----------------------------

tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI",
        "done": False
    },
    {
        "id": 2,
        "title": "Build CRUD API",
        "done": False
    },
    {
        "id": 3,
        "title": "Push to GitHub",
        "done": True
    }
]


# ----------------------------
# Root Endpoint
# ----------------------------

@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


# ----------------------------
# Health Check
# ----------------------------

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# ----------------------------
# Get All Tasks
# ----------------------------

@app.get("/tasks")
def get_tasks():
    return tasks


# ----------------------------
# Get Task by ID
# ----------------------------

@app.get("/tasks/{id}")
def get_task(id: int):

    for task in tasks:
        if task["id"] == id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {id} not found"
    )


# ----------------------------
# Create Task
# ----------------------------

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
def create_task(task: TaskCreate):

    if task.title.strip() == "":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    new_task = {
        "id": len(tasks) + 1,
        "title": task.title,
        "done": False
    }

    tasks.append(new_task)

    return new_task


# ----------------------------
# Update Task
# ----------------------------

@app.put("/tasks/{id}")
def update_task(id: int, updated_task: TaskUpdate):

    for task in tasks:

        if task["id"] == id:

            if updated_task.title.strip() == "":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Title cannot be empty"
                )

            task["title"] = updated_task.title
            task["done"] = updated_task.done

            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {id} not found"
    )


# ----------------------------
# Delete Task
# ----------------------------

@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(id: int):

    for task in tasks:

        if task["id"] == id:

            tasks.remove(task)

            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {id} not found"
    )