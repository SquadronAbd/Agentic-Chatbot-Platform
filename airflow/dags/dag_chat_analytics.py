from datetime import datetime, timedelta

import pandas as pd
from airflow.decorators import dag, task

CHATBOT_DB_URL = "postgresql://postgres:apppass@host.docker.internal:5432/chatbot_db"
PARQUET_DIR = "/tmp"

default_args = {
    "owner": "backend_team",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}


@dag(
    dag_id="dag_chat_analytics",
    default_args=default_args,
    description="Nightly: extract messages -> compute metrics -> load to analytics schema",
    schedule="0 2 * * *",
    start_date=datetime(2026, 7, 1),
    catchup=False,
    tags=["analytics", "chatbot"],
)
def dag_chat_analytics():

    @task
    def extract_messages(ds=None) -> str:
        """Read messages created in the last 24h from PostgreSQL into a DataFrame."""
        from sqlalchemy import create_engine, text

        engine = create_engine(CHATBOT_DB_URL)
        query = text("""
            SELECT m.id, m.conversation_id, m.role, m.tokens, m.created_at,
                   c.user_id
            FROM messages m
            JOIN conversations c ON c.id = m.conversation_id
            WHERE m.created_at >= NOW() - INTERVAL '1 day'
        """)
        with engine.connect() as conn:
            df = pd.read_sql(query, conn)

        raw_path = f"{PARQUET_DIR}/raw_messages_{ds}.parquet"
        df.to_parquet(raw_path, index=False)
        print(f"Extracted {len(df)} messages -> {raw_path}")
        return raw_path

    @task
    def compute_metrics(raw_path: str) -> dict:
        """Group by user_id (proxy for 'model' until a model column exists); compute
        message count, avg tokens, p95 latency."""
        df = pd.read_parquet(raw_path)
        if df.empty:
            return {"records": []}

        df["tokens"] = pd.to_numeric(df["tokens"], errors="coerce").fillna(0)

        # No per-message latency column exists yet in `messages` — placeholder until
        # the agent teammate adds one (e.g. response_time_ms). Using 0 for now.
        df["latency_ms"] = 0

        grouped = (
            df.groupby("user_id")
            .agg(
                message_count=("id", "count"),
                avg_tokens=("tokens", "mean"),
                p95_latency_ms=("latency_ms", lambda x: x.quantile(0.95)),
            )
            .reset_index()
        )
        return {"records": grouped.to_dict(orient="records")}

    @task
    def compute_daily_active_users(raw_path: str) -> int:
        """Count distinct user_ids with at least one message that day."""
        df = pd.read_parquet(raw_path)
        if df.empty:
            return 0
        return int(df["user_id"].nunique())

    @task
    def save_parquet(metrics: dict, dau: int, ds=None) -> str:
        """Write the final combined result to a Parquet file before loading."""
        records = metrics.get("records", [])
        df = pd.DataFrame(records)
        df["date"] = ds
        df["daily_active_users"] = dau

        out_path = f"{PARQUET_DIR}/metrics_{ds}.parquet"
        df.to_parquet(out_path, index=False)
        print(f"Saved final metrics -> {out_path}")
        return out_path

    @task
    def load_to_postgres(parquet_path: str):
        """Upsert Parquet data into the daily_chat_metrics analytics table."""
        from sqlalchemy import create_engine, text

        df = pd.read_parquet(parquet_path)
        if df.empty:
            print("No records to load.")
            return

        engine = create_engine(CHATBOT_DB_URL)
        with engine.begin() as conn:
            for _, row in df.iterrows():
                conn.execute(
                    text("""
                        INSERT INTO daily_chat_metrics
                            (date, user_id, message_count, avg_tokens, p95_latency_ms, daily_active_users)
                        VALUES
                            (:date, :user_id, :message_count, :avg_tokens, :p95_latency_ms, :daily_active_users)
                        ON CONFLICT (date, user_id) DO UPDATE
                        SET message_count = EXCLUDED.message_count,
                            avg_tokens = EXCLUDED.avg_tokens,
                            p95_latency_ms = EXCLUDED.p95_latency_ms,
                            daily_active_users = EXCLUDED.daily_active_users
                    """),
                    {
                        "date": row["date"],
                        "user_id": row["user_id"],
                        "message_count": int(row["message_count"]),
                        "avg_tokens": float(row["avg_tokens"]),
                        "p95_latency_ms": float(row["p95_latency_ms"]),
                        "daily_active_users": int(row["daily_active_users"]),
                    },
                )
        print(f"Loaded {len(df)} rows into daily_chat_metrics")

    raw = extract_messages()
    metrics = compute_metrics(raw)
    dau = compute_daily_active_users(raw)
    final = save_parquet(metrics, dau)
    load_to_postgres(final)


dag_chat_analytics()