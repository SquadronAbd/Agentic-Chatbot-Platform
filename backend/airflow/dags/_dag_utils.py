"""Shared configuration for Airflow DAGs in the chatbot platform."""

from datetime import timedelta

default_args = {
    "owner": "data-eng",
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

CHATBOT_DB_URL = (
    "postgresql://postgres:apppass@host.docker.internal:5434/chatbot_db"
)

PARQUET_DIR = "/tmp"
REPORTS_DIR = "/tmp/reports"

COST_PER_1000_TOKENS = 0.002
