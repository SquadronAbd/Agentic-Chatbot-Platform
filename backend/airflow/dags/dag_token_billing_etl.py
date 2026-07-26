"""Weekly ETL: aggregate token usage and export a CSV billing report."""

from __future__ import annotations

import os
from datetime import datetime, timedelta
from typing import Any

import pandas as pd
from airflow.decorators import dag, task

from _dag_utils import (
    CHATBOT_DB_URL,
    COST_PER_1000_TOKENS,
    PARQUET_DIR,
    REPORTS_DIR,
    default_args,
)


def _previous_calendar_week_bounds(ds: str) -> tuple[datetime, datetime]:
    """Return [week_start, week_end) for the calendar week before the DAG run date.

    When the DAG runs on a Monday, *ds* is that Monday. The reporting window is the
    prior Monday 00:00:00 through the following Sunday 23:59:59 (exclusive upper bound
    is the run-date Monday at 00:00:00).
    """
    run_monday = datetime.strptime(ds, "%Y-%m-%d")
    week_start = run_monday - timedelta(days=7)
    week_end_exclusive = run_monday
    return week_start, week_end_exclusive


@dag(
    dag_id="dag_token_billing_etl",
    default_args=default_args,
    description=(
        "Weekly ETL: aggregate AI token usage per user, estimate costs, "
        "and export a CSV billing report for administrators"
    ),
    schedule=None,
    start_date=datetime(2026, 7, 1),
    catchup=False,
    max_active_runs=1,
    tags=["billing", "analytics", "etl"],
)
def dag_token_billing_etl():
    """Weekly token billing pipeline — read-only analytics over stored usage data."""

    @task
    def extract_token_usage(ds: str | None = None) -> str:
        """Extract messages from the previous calendar week into a Parquet file."""
        from sqlalchemy import create_engine, text

        week_start, week_end = _previous_calendar_week_bounds(ds)

        engine = create_engine(CHATBOT_DB_URL)
        query = text("""
            SELECT
                m.id,
                m.conversation_id,
                m.role,
                m.tokens,
                m.created_at,
                c.user_id,
                u.email,
                u.full_name
            FROM messages m
            JOIN conversations c ON c.id = m.conversation_id
            JOIN users u ON u.id = c.user_id
            WHERE m.created_at >= :week_start
              AND m.created_at < :week_end
        """)
        with engine.connect() as conn:
            df = pd.read_sql(
                query,
                conn,
                params={"week_start": week_start, "week_end": week_end},
            )

        if not df.empty:
            df["id"] = df["id"].astype(str)
            df["conversation_id"] = df["conversation_id"].astype(str)
            df["user_id"] = df["user_id"].astype(str)

        raw_path = f"{PARQUET_DIR}/raw_token_usage_{ds}.parquet"
        df.to_parquet(raw_path, index=False)
        print(
            f"Extracted {len(df)} messages for "
            f"{week_start.date()} – {week_end.date() - timedelta(days=1)} -> {raw_path}"
        )
        return raw_path

    @task
    def compute_billing(raw_path: str) -> dict[str, Any]:
        """Aggregate token usage per user and estimate billing costs."""
        df = pd.read_parquet(raw_path)
        if df.empty:
            print("No messages found for the reporting period.")
            return {"records": []}

        df["tokens"] = pd.to_numeric(df["tokens"], errors="coerce").fillna(0)

        grouped = (
            df.groupby(["user_id", "email", "full_name"], dropna=False)
            .agg(
                total_messages=("id", "count"),
                total_tokens=("tokens", "sum"),
                average_tokens_per_message=("tokens", "mean"),
            )
            .reset_index()
        )

        grouped["estimated_cost"] = (
            (grouped["total_tokens"] / 1000) * COST_PER_1000_TOKENS
        ).round(4)

        grouped["total_tokens"] = grouped["total_tokens"].astype(int)
        grouped["average_tokens_per_message"] = grouped[
            "average_tokens_per_message"
        ].round(4)

        records = grouped.to_dict(orient="records")
        print(f"Computed billing for {len(records)} users")
        return {"records": records}

    @task
    def export_csv(billing: dict[str, Any], ds: str | None = None) -> str:
        """Export the aggregated billing report as a CSV file."""
        os.makedirs(REPORTS_DIR, exist_ok=True)

        records = billing.get("records", [])
        columns = [
            "user_id",
            "email",
            "full_name",
            "total_messages",
            "total_tokens",
            "average_tokens_per_message",
            "estimated_cost",
        ]
        df = pd.DataFrame(records, columns=columns)

        report_date = ds.replace("-", "_") if ds else datetime.utcnow().strftime("%Y_%m_%d")
        csv_path = f"{REPORTS_DIR}/token_billing_{report_date}.csv"
        df.to_csv(csv_path, index=False)
        print(f"Exported billing report -> {csv_path} ({len(df)} rows)")
        return csv_path

    @task
    def log_summary(billing: dict[str, Any], csv_path: str) -> None:
        """Log aggregate billing statistics and the exported CSV location."""
        records = billing.get("records", [])
        if not records:
            print(
                "Billing summary: 0 users, 0 messages, 0 tokens, "
                f"$0.0000 estimated cost. CSV: {csv_path}"
            )
            return

        total_messages = sum(r["total_messages"] for r in records)
        total_tokens = sum(r["total_tokens"] for r in records)
        total_cost = round(sum(r["estimated_cost"] for r in records), 4)

        print("Billing summary:")
        print(f"  Users processed:     {len(records)}")
        print(f"  Total messages:      {total_messages}")
        print(f"  Total tokens:        {total_tokens}")
        print(f"  Total estimated cost: ${total_cost:.4f}")
        print(f"  CSV file location:   {csv_path}")

    raw = extract_token_usage()
    billing = compute_billing(raw)
    csv_path = export_csv(billing)
    log_summary(billing, csv_path)


dag_token_billing_etl()
