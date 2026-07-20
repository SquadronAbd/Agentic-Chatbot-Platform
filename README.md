# Agentic Chatbot Platform — Backend Setup

This backend uses FastAPI + PostgreSQL (via Docker) + Alembic migrations.
Follow these steps after cloning the repo — no local PostgreSQL install needed.

## Prerequisites
- Docker Desktop installed and running
- Python 3.11 or 3.12 recommended (3.14 is very new and some packages, like
  `psycopg2-binary`, may not yet have pre-built wheels for it — if you hit a
  "Microsoft Visual C++ 14.0 required" error during `pip install`, either
  switch to Python 3.12, or run `pip install psycopg2-binary --upgrade` to
  fetch a newer wheel)

## Setup steps

1. Clone the repo and move into the backend folder:
   ```
   git clone <repo-url>
   cd backend
   ```

2. Create your own `.env` file from the template:
   ```
   copy .env.example .env
   ```
   (Mac/Linux: `cp .env.example .env`)
   The default values already match `docker-compose.yml` — no changes needed
   unless you're customizing ports/credentials.

3. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Start Postgres and Redis containers:
   ```
   docker-compose up -d
   ```
   Confirm both are running:
   ```
   docker ps
   ```
   You should see `chatbot_db` and `chatbot_redis`.

5. Apply all database migrations (this creates every table):
   ```
   alembic upgrade head
   ```

6. Run the API server:
   ```
   uvicorn app.main:app --reload
   ```

7. Open `http://localhost:8000/docs` and confirm:
   - `/health` returns `{"status": "ok"}`
   - `/health/db` returns `{"status": "ok", "database": "connected"}`

## Database credentials (local Docker only — not real secrets)

- User: `postgres`
- Password: `apppass`
- Database: `chatbot_db`
- Port: `5432`

## When someone changes the database schema

If you add/edit a model:
```
alembic revision --autogenerate -m "describe your change"
```
Commit the new file created under `alembic/versions/`.

Everyone else, after pulling your change, just runs:
```
alembic upgrade head
```
This applies only the new migration(s) — already-applied ones are skipped automatically.

## Useful commands

| Command | What it does |
|---|---|
| `alembic current` | Shows which migration your DB is currently at |
| `alembic history` | Lists all migrations in order |
| `docker-compose down` | Stops containers (data persists in the volume) |
| `docker-compose down -v` | Stops containers AND wipes the database volume (fresh start) |
| `docker exec -it chatbot_db psql -U postgres -d chatbot_db` | Open a direct SQL prompt into the database |
| `docker exec -it chatbot_db psql -U postgres -d chatbot_db -c "\dt"` | List all tables |

## Project structure

```
backend/
├── app/
│   ├── main.py          # FastAPI app + health check routes
│   ├── config.py        # Loads settings from .env
│   ├── database.py      # SQLAlchemy engine/session setup
│   ├── models/           # All 8 SQLAlchemy models + message_chunks join table
│   ├── schemas/          # Pydantic request/response schemas (in progress)
│   ├── routers/          # API route definitions (in progress)
│   └── core/
│       ├── security.py  # Password hashing, JWT — done
│       └── deps.py      # Auth/RBAC dependencies — done
├── alembic/              # Migration history — do not edit existing files
├── .env                  # Your local secrets — NOT committed
├── .env.example          # Template — committed, no real secrets
├── requirements.txt
└── docker-compose.yml
```