-- Runs once on first container startup (docker-entrypoint-initdb.d)
-- Creates both databases and enables pgvector extension.
-- The financial_rag data is restored separately by init-restore.sh

CREATE EXTENSION IF NOT EXISTS vector;
CREATE DATABASE chatbot_db;
