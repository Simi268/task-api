from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI(
    title="Task Management API",
    description="""
A simple RESTful CRUD API built using FastAPI.

### Features
- Create Tasks
- Read All Tasks
- Read Task by ID
- Update Tasks
- Delete Tasks

Built as part of the Backend AI Engineering Week 2 Assignment.
""",
    version="1.0.0",
    
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
# In-Memory Database
# =====================================================

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


# =====================================================
# Root Endpoint
# =====================================================

@app.get(
    "/",
    summary="API Information",
    description="Returns basic information about the Task Management API."
)
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": [
            "/tasks"
        ]
    }


# =====================================================
# Health Check
# =====================================================

@app.get(
    "/health",
    summary="Health Check",
    description="Checks whether the API server is running."
)
def health():
    return {
        "status": "ok"
    }


# =====================================================
# Get All Tasks
# =====================================================

@app.get(
    "/tasks",
    summary="Get All Tasks",
    description="Returns the complete list of tasks."
)
def get_tasks():
    return tasks


# =====================================================
# Get Task By ID
# =====================================================

@app.get(
    "/tasks/{id}",
    summary="Get Task By ID",
    description="Returns a single task using its unique ID."
)
def get_task(id: int):

    for task in tasks:
        if task["id"] == id:
            return task

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {id} not found"
    )


# =====================================================
# Create Task
# =====================================================

@app.post(
    "/tasks",
    status_code=status.HTTP_201_CREATED,
    summary="Create Task",
    description="Creates a new task."
)
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


# =====================================================
# Update Task
# =====================================================

@app.put(
    "/tasks/{id}",
    summary="Update Task",
    description="Updates the title and completion status of a task."
)
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


# =====================================================
# Delete Task
# =====================================================

@app.delete(
    "/tasks/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Task",
    description="Deletes a task using its ID."
)
def delete_task(id: int):

    for task in tasks:

        if task["id"] == id:

            tasks.remove(task)

            return

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Task {id} not found"
    )