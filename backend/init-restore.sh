#!/bin/bash
# Runs once on first container startup, after init-db.sql.
# Restores the pre-populated financial_rag dump so teammates
# don't need to run ingest.py manually.

DUMP_FILE="/docker-entrypoint-initdb.d/financial_rag.dump"

if [ -f "$DUMP_FILE" ]; then
    echo "Restoring financial_rag from dump..."
    pg_restore -U "$POSTGRES_USER" -d financial_rag -v "$DUMP_FILE"
    echo "Restore complete."
else
    echo "No dump file found at $DUMP_FILE — skipping restore."
fi
