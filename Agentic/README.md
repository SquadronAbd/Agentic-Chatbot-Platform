# Agentic RAG — Setup & Evaluation Guide

Multi-Agent Retrieval-Augmented Generation pipeline built with LangGraph, Groq LLM, and PostgreSQL + pgvector.

---

## Prerequisites

- Python 3.10+
- PostgreSQL with pgvector extension running (Docker recommended)
- Groq API key

---

## 1. Environment Setup

Create a virtual environment and install dependencies:

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

Create a `.env` file inside the `Agentic/` folder:

```env
GROQ_API_KEY=your_groq_api_key_here
LLM_MODEL=llama-3.3-70b-versatile
EMBEDDING_MODEL=BAAI/bge-small-en-v1.5
DATABASE_URL=postgresql+psycopg://postgres:password@localhost:5432/financial_rag
COLLECTION_NAME=documents
GOOGLE_API_KEY=
```

---

## 2. Start PostgreSQL with pgvector

```bash
docker run -d \
  --name pgvector \
  -e POSTGRES_PASSWORD=password \
  -e POSTGRES_DB=financial_rag \
  -p 5432:5432 \
  pgvector/pgvector:pg16
```

---

## 3. Ingest Documents (One-Time)

Ingest the 100 financial markdown reports into PostgreSQL. This only needs to be run once — the vectors are stored persistently.

```bash
python ingest.py --dir ../backend/data/markdowns --clear
```

This will:
- Load and chunk all markdown files
- Generate embeddings using `BAAI/bge-small-en-v1.5` (local, CPU)
- Store 82,000+ chunks in PostgreSQL via pgvector
- Takes approximately 1.5–2 hours on first run

---

## 4. Run the Multi-Agent RAG Server

From inside the `Agentic/` folder:

```bash
uvicorn app.main:app --reload
```

The server starts at `http://localhost:8000`. On startup it:
- Loads the embedding model and cross-encoder reranker
- Bootstraps the BM25 corpus from PostgreSQL (instant after initial ingest)

### API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | Health check |
| POST | `/chat` | Send a question, get an AI answer |
| POST | `/ingest` | Upload a file for ingestion |

### Example Chat Request

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id": "test-123", "question": "What were Apple revenue in 2023?"}'
```

---

## 5. Agent Architecture

The pipeline routes each query through a LangGraph workflow:

```
User Query
    │
    ▼
Router Agent         — classifies intent (financial vs general)
    │
    ├── General Agent       — handles greetings / off-topic
    │
    └── Planner Agent       — breaks down financial queries
            │
            ▼
        Document Agent      — hybrid retrieval (BM25 + pgvector + reranker)
            │
            ▼
        Memory Agent        — injects conversation history
            │
            ▼
        Tool Agent          — runs calculator, datetime, SQL tools
            │
            ▼
        Reflection Agent    — validates and refines the answer
            │
            ▼
        Final Response
```

### Models Used

| Role | Model |
|------|-------|
| LLM | `llama-3.3-70b-versatile` via Groq |
| Embedding | `BAAI/bge-small-en-v1.5` (local, CPU) |
| Reranker | `cross-encoder/ms-marco-MiniLM-L-6-v2` (local, CPU) |

---

## 6. Run DeepEval Evaluation

The evaluation script sends questions to the running RAG server and scores each answer using `AnswerRelevancyMetric` and `FaithfulnessMetric` with Groq as the LLM judge.

**The RAG server must be running before starting evaluation.**

### Run on a random sample of 10 questions

```bash
python evaluate.py --questions ..\backend\data\questions\questions.json --sample 10
```

### Run on all questions

```bash
python evaluate.py --questions ..\backend\data\questions\questions.json --all
```

### Run with a custom pass/fail threshold (default: 0.7)

```bash
python evaluate.py --questions ..\backend\data\questions\questions.json --sample 10 --threshold 0.5
```

### Save results to a custom file

```bash
python evaluate.py --questions ..\backend\data\questions\questions.json --sample 10 --output results_run1.json
```

### Sample Output

```
Evaluating 10 questions  (host=http://localhost:8000  threshold=0.7)
============================================================

[1/10] Did Incitec Pivot Limited mention any mergers or acquisitions...
  → Answer: Yes, Incitec Pivot Limited mentioned the acquisition of...
  ✓ AnswerRelevancyMetric          score=1.000
  ✓ FaithfulnessMetric             score=1.000

[2/10] What was the Gross margin (%) for Ritchie Bros...
  ⚠ Empty answer — skipping

============================================================
SUMMARY
============================================================
  AnswerRelevancyMetric          avg=0.952  pass_rate=86%  (6/7)
  FaithfulnessMetric             avg=1.000  pass_rate=100%  (7/7)

Results saved → eval_results.json
```

### Metrics Explained

| Metric | What it measures |
|--------|-----------------|
| **AnswerRelevancy** | Does the answer actually address the question? |
| **Faithfulness** | Are all claims in the answer grounded in the retrieved context? |

Results are saved to `eval_results.json` with the full answer and scores for each question.

---

## 7. Swagger UI

Interactive API docs available at:

```
http://localhost:8000/docs
```
