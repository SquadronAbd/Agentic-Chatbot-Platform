-- Runs once on first container startup (docker-entrypoint-initdb.d)
-- Creates both databases and enables pgvector extension.
-- The financial_rag data is restored separately by init-restore.sh

-- =============================================================
-- Runs ONCE on first container startup (docker-entrypoint-initdb.d)
-- Executes in the context of POSTGRES_DB (financial_rag)
-- =============================================================

-- 1. Enable pgvector in financial_rag (AI teammate's RAG database)
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Create the backend application database
CREATE DATABASE chatbot_db;

-- 3. Connect to chatbot_db and enable pgvector there too
\connect chatbot_db;
CREATE EXTENSION IF NOT EXISTS vector;