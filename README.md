# Enterprise Agentic RAG Platform — FinRAG

An enterprise-grade **Multi-Agent Retrieval-Augmented Generation (RAG)** platform for intelligent analysis of financial documents. Users upload their own documents and query them through a conversational AI interface with real-time streaming responses.

Built with **LangGraph**, the platform orchestrates specialized AI agents for intent classification, document retrieval, planning, and reflection. Retrieval uses a hybrid dense + BM25 pipeline with cross-encoder reranking, HNSW indexing, and document-scoped filtering.

---

## Features

- **Multi-Agent LangGraph Workflow** — intent classifier routes to General, Document, or Planner agent; Reflection agent validates every answer
- **Hybrid Retrieval** — semantic (pgvector HNSW) + BM25 merged via Reciprocal Rank Fusion, reranked with a cross-encoder
- **Document-Scoped Retrieval** — "this document" queries are scoped to the user's own uploaded files via Redis-tracked source paths
- **Adaptive Chunking** — markdown-header-aware two-pass chunker; sentence-boundary splits; short PDF page bypass; noise chunk filter
- **Asymmetric BGE Embeddings** — query prefix applied at search time; documents encoded without prefix for better recall
- **Disk-Backed Embedding Cache** — `CacheBackedEmbeddings` on `LocalFileStore`; re-uploading the same document is instant
- **Redis-Backed Session Memory** — 24h conversation memory per session with in-memory fallback
- **Content-Hash Dedup on Ingest** — unchanged files are skipped; updated files delete old chunks before reingest
- **Real-Time Streaming Chat** — WebSocket with per-word streaming; automatic reconnect; token expiry redirect
- **Document Upload with Progress** — background ingestion pipeline with stage callbacks (ingesting → chunking → embedding → ready)
- **LLM Response Cache** — SQLite-backed global cache; identical prompts served from disk without Groq API calls
- **LLM Retry** — exponential backoff with jitter (3 attempts) on Groq API failures
- **JWT Authentication + RBAC** — access / refresh tokens; role-based endpoints (admin, manager, agent, viewer)
- **Airflow Analytics DAGs** — scheduled maintenance and analytics pipelines
- **Docker Compose Deployment** — single command to start all services behind Nginx

---

## System Architecture

```
User Browser
     │  WebSocket / REST
     ▼
  Nginx (reverse proxy, port 80)
     │
     ├── /api/v1/  ──► FastAPI Backend (port 8000)
     │                      │  JWT auth, conversations, document management
     │                      │  HTTP POST to agentic /chat and /ingest
     │                      ▼
     │               Agentic AI Service (port 8001)
     │                      │
     │               LangGraph Workflow
     │                      │
     │        ┌─────────────┼─────────────┐
     │        ▼             ▼             ▼
     │   General Agent  Document Agent  Planner Agent
     │                      │
     │               Hybrid Retriever
     │               ├── pgvector HNSW (semantic)
     │               ├── BM25 (keyword)
     │               ├── RRF merge
     │               └── Cross-encoder rerank
     │
     ├── /  ──────────► Next.js Frontend (port 3000)
     │
PostgreSQL + pgvector  ◄── vector embeddings + app tables
Redis                  ◄── sessions, doc source registry
Airflow                ◄── analytics DAGs (port 8080)
```

---

## Agent Workflow

```
User Query
     │
     ▼
Intent Classifier (LLM)
     │
     ├── "general" ──────────► General Agent ──────────────────┐
     ├── "document" ─────────► Document Agent                  │
     │                              │                           │
     │                         Hybrid Retriever                 │
     │                         (source-filtered if              │
     │                          "this document" detected)       │
     │                              │                           │
     └── "planner" ─────────► Planner Agent                    │
                                    │                           │
                              Step decomposition                │
                              → Document + General agents       │
                                    │                           │
                                    ▼                           │
                            Reflection Agent ◄──────────────────┘
                                    │
                              Final Response
```

---

## Retrieval Pipeline

```
Query
  │
  ├── Step-back transformer (LLM) → abstract query
  │
  ├── Semantic search  (pgvector HNSW, cosine similarity)
  │     original query + abstract query → deduplicated
  │
  ├── BM25 keyword search
  │     original query + abstract query → deduplicated
  │
  ├── Weighted RRF merge
  │     conceptual queries: semantic=0.7, bm25=0.3
  │     specific financial (amounts, tickers): semantic=0.3, bm25=0.7
  │
  ├── Cross-encoder reranking (ms-marco-MiniLM-L-6-v2)
  │
  └── Page-based context expansion (PDFs only)
```

---

## Technology Stack

### AI / LLM

| Component | Technology |
|-----------|-----------|
| LLM | `llama-3.3-70b-versatile` via Groq |
| Embedding | `BAAI/bge-small-en-v1.5` (local CPU, batch_size=128) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` (local CPU) |
| Orchestration | LangGraph |
| LLM Framework | LangChain |
| LLM Cache | LangChain SQLiteCache |
| Embedding Cache | LangChain CacheBackedEmbeddings + LocalFileStore |

### Backend

| Component | Technology |
|-----------|-----------|
| API Framework | FastAPI |
| ORM | SQLAlchemy (async) |
| Migrations | Alembic |
| Auth | JWT (access + refresh tokens) |
| Vector DB | PostgreSQL + pgvector (HNSW index) |
| App DB | PostgreSQL |
| Cache / Sessions | Redis |
| HTTP Client | httpx (async) |
| Task Queue | FastAPI BackgroundTasks |
| Analytics | Apache Airflow |

### Frontend

| Component | Technology |
|-----------|-----------|
| Framework | Next.js 14 (App Router) |
| State | Zustand (persist middleware) |
| Styling | Tailwind CSS |
| Chat | WebSocket with streaming |
| Data Fetching | TanStack Query |

### Infrastructure

| Component | Technology |
|-----------|-----------|
| Reverse Proxy | Nginx |
| Containerization | Docker + Docker Compose |
| Embedding Volume | Docker named volume (`embedding_cache`) |

---

## Project Structure

```
Agentic-Chatbot-Platform/
├── Agentic/                        # AI service (port 8001)
│   └── app/
│       ├── agents/                 # General, Document, Planner, Reflection
│       ├── graph/                  # LangGraph workflow, state, nodes, edges
│       ├── memory/                 # Redis-backed session manager, summarizer
│       ├── models/                 # LLM, embeddings (cached), vector store
│       ├── prompts/                # Prompt builder
│       ├── rag/                    # Retriever, chunker, pipeline, BM25, doc_store
│       ├── router/                 # Intent classifier
│       ├── tools/                  # RetrieverTool, ToolManager
│       ├── user_ingestion/         # UploadService, DocumentParser
│       └── main.py                 # FastAPI app, lifespan (HNSW init, BM25 bootstrap)
│
├── backend/                        # Application backend (port 8000)
│   └── app/
│       ├── api/v1/                 # chat, documents, auth, users endpoints
│       ├── core/                   # config, security, database, deps
│       ├── models/                 # SQLAlchemy ORM models
│       ├── repositories/           # DB access layer
│       ├── services/               # DocumentService, auth logic
│       └── airflow/dags/           # Airflow analytics DAGs
│
├── frontend/                       # Next.js app (port 3000)
│   ├── app/                        # App Router pages
│   ├── components/                 # chat, ui, sidebar, documents
│   ├── hooks/                      # use-chat-stream (WebSocket), use-api
│   └── store/                      # Zustand stores (auth, chat, ui)
│
├── nginx.conf                      # Reverse proxy config
├── docker-compose.yml              # All services
└── README.md
```

---

## Quickstart (Docker)

### Prerequisites

- Docker and Docker Compose installed
- Groq API key

### 1. Clone

```bash
git clone https://github.com/SquadronAbd/Agentic-Chatbot-Platform.git
cd Agentic-Chatbot-Platform
```

### 2. Configure environment

Create `Agentic/.env`:

```env
GROQ_API_KEY=your_groq_api_key
LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
COLLECTION_NAME=documents
DATABASE_URL=postgresql+psycopg://postgres:password@pgvector:5432/financial_rag
REDIS_URL=redis://redis:6379/0
```

Create `backend/.env`:

```env
SECRET_KEY=your_secret_key
DATABASE_URL=postgresql+asyncpg://postgres:password@pgvector:5432/chatbot_db
REDIS_URL=redis://redis:6379/0
AI_SERVICE_URL=http://agentic:8000
BACKEND_INTERNAL_URL=http://backend:8000
INTERNAL_API_KEY=your_internal_key
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

### 3. Start all services

```bash
docker compose up --build -d
```

Services started:

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| Backend API | http://localhost/api/v1 |
| Agentic AI | http://localhost:8001 |
| Airflow | http://localhost:8080 |

### 4. Upload documents and chat

1. Register / log in at `http://localhost`
2. Upload a financial document (PDF, TXT, MD — up to 50 MB)
3. Wait for status to change to **Ready**
4. Ask questions in the chat

---

## Database

| Store | Purpose |
|-------|---------|
| PostgreSQL (`chatbot_db`) | Users, conversations, messages, documents |
| PostgreSQL (`financial_rag`) | pgvector chunk embeddings (HNSW indexed) |
| Redis | Conversation sessions (24h TTL), user document source registry |
| LocalFileStore (`/tmp/embedding_cache`) | Disk-backed embedding cache (Docker volume) |
| SQLite (`/tmp/llm_cache.db`) | LLM response cache |

---

## Example Questions

- Which company does this document belong to?
- Summarize the key financial highlights from this report.
- What were the operating expenses in Q3?
- Compare revenue growth over the last three fiscal years.
- What business risks are disclosed in the filing?
- What is the company's cash flow position?
- Explain the management discussion section.
- What acquisitions were completed during the fiscal year?

---

## Use Cases

- Financial report summarization and Q&A
- SEC filing analysis
- Enterprise knowledge retrieval from uploaded documents
- Investment research assistance
- Risk and compliance review
- Earnings analysis

---

## License

This project is intended for educational and research purposes.

---

## Acknowledgements

LangChain · LangGraph · FastAPI · PostgreSQL · pgvector · HuggingFace · Next.js · Docker · Groq · Redis · Apache Airflow

Dataset: https://www.kaggle.com/datasets/rrr3try/enterprise-rag-markdown
