# Task Management API

A RESTful CRUD API built using FastAPI and SQLite for the Backend AI Engineering assignment.

The API supports complete task management with persistent database storage. Tasks are stored in SQLite, so data survives application restarts.

## Features

- Create, Read, Update, and Delete tasks
- SQLite database persistence
- Automatic database and table creation
- Automatic seed data on first run
- Input validation
- Parameterized SQL queries
- Proper HTTP status codes
- Interactive Swagger UI documentation

## Tech Stack

- Python
- FastAPI
- SQLite
- Pydantic
- Uvicorn

## Database

The project uses **SQLite** for persistent task storage.

SQLite was chosen because it:

- Stores the database in a single file
- Requires no separate database server
- Requires minimal setup
- Provides persistent storage across application restarts

The database is stored locally as:

`tasks.db`

The application automatically creates `tasks.db` and the `tasks` table when the server starts if they do not already exist.

If the `tasks` table is empty, three example tasks are seeded automatically. The database file is ignored by Git so that each fresh clone creates its own database.

### Tasks Table

The `tasks` table contains:

| Column | Type | Description |
|--------|------|-------------|
| `id` | INTEGER | Primary key |
| `title` | TEXT | Task title |
| `done` | INTEGER | Completion status (`0` or `1`) |

## Installation

Clone the repository:

```bash
git clone https://github.com/Simi268/task-api.git
cd task-api
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux/macOS**

```bash
source venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

## Run the API

Start the server:

```bash
uvicorn main:app --reload
```

The database and `tasks` table will be created automatically when the application starts.

Open:

- API: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | API Information |
| GET | `/health` | Health Check |
| GET | `/tasks` | Get all tasks |
| GET | `/tasks/{id}` | Get task by ID |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |

## SQL Exploration

The database was also explored directly using DB Browser for SQLite.

Example query:

```sql
SELECT * FROM tasks WHERE done = 1;
```

This query returns all completed tasks, where `done` is stored as `1`.

Other SQL operations tested include:

```sql
SELECT * FROM tasks;

SELECT COUNT(*) FROM tasks;

UPDATE tasks SET done = 1;

DELETE FROM tasks WHERE done = 1;
```

Changes made directly in SQLite are reflected by the API because both the API and DB Browser operate on the same database file.

## Database Screenshot

The following screenshot shows the SQLite database and SQL queries explored using DB Browser for SQLite.

![SQLite Database](docs/image.png)

## Swagger UI

![Swagger UI](docs/swagger.png)

## Persistence

Tasks are stored in SQLite rather than an in-memory Python list.

This means tasks created or updated through the API remain available after the FastAPI server is stopped and restarted.

The database is created automatically on a fresh project setup, so no manual database configuration is required.

## Project Structure

```text
task-api/
│
├── docs/
│   ├── swagger.png
│   └── image.png
│
├── main.py
├── requirements.txt
├── README.md
├── .gitignore
└── tasks.db          # Created automatically and ignored by Git
```

## HTTP Status Codes

The API uses appropriate HTTP status codes:

- `200 OK` — successful read or update
- `201 Created` — task successfully created
- `204 No Content` — task successfully deleted
- `400 Bad Request` — invalid input
- `404 Not Found` — task does not exist