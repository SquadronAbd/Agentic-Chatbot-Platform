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

## Airflow (analytics pipeline)

This project includes one working DAG — `dag_chat_analytics` — which nightly
extracts messages, computes usage metrics, and loads them into the
`daily_chat_metrics` table.

After running `docker-compose up -d` (Step 4 above), Airflow comes up
alongside Postgres/Redis automatically. No separate setup needed.

1. Wait ~2-3 minutes on first run — Airflow pulls its image and installs
   `pandas`/`sqlalchemy`/`psycopg2-binary`/`pyarrow` inside its containers.
2. Open the Airflow UI: `http://localhost:8080`
3. Log in: `admin` / `admin`
4. Find `dag_chat_analytics` in the DAGs list, toggle it **on** (unpaused)
5. Click the ▶ (trigger) button to run it manually instead of waiting for
   its 2 AM schedule
6. Click into the run — all 5 tasks should turn green:
   `extract_messages -> compute_metrics -> compute_daily_active_users ->
   save_parquet -> load_to_postgres`

Verify data landed:
```
docker exec -it chatbot_db psql -U postgres -d chatbot_db -c "SELECT * FROM daily_chat_metrics;"
```

If the table is empty, that's expected until real conversations/messages
exist in `chatbot_db` — the DAG runs successfully either way.

## Managing the Airflow containers

| Command | What it does |
|---|---|
| `docker stop airflow_webserver airflow_scheduler airflow_db` | Pause Airflow, keep main app DB/Redis running |
| `docker start airflow_db airflow_scheduler airflow_webserver` | Resume Airflow (start in this order) |
| `docker-compose down` | Stop everything, keep all data |
| `docker-compose down -v` | Stop everything AND wipe all data (fresh start) |



````md
## Backend Structure

```text
backend/
│
├── app/
│   ├── main.py
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   ├── security.py
│   │   └── deps.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── routers/
│   └── services/
│
├── airflow/
├── alembic/
├── data/
├── tests/
├── requirements.txt
├── docker-compose.yml
├── Dockerfile
└── README.md

```