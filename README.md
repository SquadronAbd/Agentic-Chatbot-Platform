# 🤖 Enterprise Agentic RAG Platform for Financial Report Analysis

An enterprise-grade **Multi-Agent Retrieval-Augmented Generation (RAG)** platform designed for intelligent analysis of enterprise financial reports.

Built with **LangGraph**, the platform orchestrates multiple specialized AI agents that collaboratively retrieve, reason, validate, and generate context-aware responses from financial documents. Unlike traditional RAG systems that rely on a single LLM pipeline, this platform follows an **agentic architecture**, where each agent is responsible for a dedicated task such as planning, routing, document retrieval, memory management, reflection, and tool execution.

The system utilizes **PostgreSQL + pgvector** for semantic retrieval, enabling efficient vector similarity search over embedded financial reports.

---

# 🚀 Features

- 🤖 Multi-Agent AI Architecture powered by LangGraph
- 📄 Enterprise Financial Report Analysis
- 🔍 Retrieval-Augmented Generation (RAG)
- 🧠 Semantic Search using PostgreSQL + pgvector
- 💬 Context-Aware Conversational Chat
- 📝 Multi-turn Conversation Memory
- 🔄 Reflection-based Response Validation
- 🛠️ Tool-Augmented Reasoning
- 📂 Markdown Financial Document Processing
- 🔐 JWT Authentication & Role-Based Access Control
- 📊 Modern Analytics Dashboard
- ⚡ FastAPI Backend
- 🌐 React / Next.js Frontend
- 🐳 Dockerized Deployment

---

# 🏗️ System Architecture

```text
                             ┌───────────────────────────┐
                             │   React / Next.js Client  │
                             └─────────────┬─────────────┘
                                           │
                                           ▼
                               FastAPI REST Backend
                                           │
                                           ▼
                          LangGraph Agent Orchestrator
                                           │
        ┌──────────────┬─────────────┬─────────────┬──────────────┐
        ▼              ▼             ▼             ▼              ▼
   Router Agent   Planner Agent  Memory Agent  Tool Agent  General Agent
        │
        ▼
 Document Retrieval Agent
        │
        ▼
 Reflection Agent
        │
        ▼
 Final AI Response
        │
        ▼
 PostgreSQL + pgvector
        │
        ▼
 Financial Reports Dataset
```

---

# 🧠 Multi-Agent Architecture

Unlike conventional chatbots, this platform distributes responsibilities across specialized AI agents coordinated through **LangGraph**.

| Agent | Responsibility |
|--------|----------------|
| **Agent Manager** | Coordinates the complete workflow and manages agent state transitions. |
| **Router Agent** | Identifies user intent and routes requests to the appropriate workflow. |
| **Planner Agent** | Decomposes complex financial queries into logical reasoning steps. |
| **Document Agent** | Retrieves relevant financial report sections using semantic similarity search over pgvector embeddings. |
| **Memory Agent** | Maintains conversational context and previous interactions for coherent multi-turn conversations. |
| **Tool Agent** | Executes external tools and utility functions whenever additional computation or retrieval is required. |
| **Reflection Agent** | Reviews generated responses to improve factual consistency and completeness before returning them to the user. |
| **General Agent** | Handles greetings, casual conversations, and general-purpose queries that do not require document retrieval. |

---

# 🔄 Agent Workflow

```text
                User Query
                     │
                     ▼
              Router Agent
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
General Conversation      Financial Query
        │                         │
        ▼                         ▼
 General Agent             Planner Agent
                                  │
                                  ▼
                         Document Agent
                                  │
                                  ▼
                     PostgreSQL + pgvector
                                  │
                                  ▼
                        Retrieved Context
                                  │
                                  ▼
                           Memory Agent
                                  │
                                  ▼
                            Tool Agent
                                  │
                                  ▼
                        Reflection Agent
                                  │
                                  ▼
                           Final Response
```

---

# 🔍 Retrieval-Augmented Generation Pipeline

The chatbot follows a Retrieval-Augmented Generation workflow specifically optimized for enterprise financial reports.

1. User submits a financial query.
2. Router Agent determines the query type.
3. Planner Agent formulates the retrieval strategy.
4. Document Agent generates embeddings and retrieves relevant report sections from PostgreSQL + pgvector.
5. Memory Agent incorporates previous conversational context.
6. Tool Agent executes any required utilities.
7. Reflection Agent validates and refines the generated answer.
8. The final response is returned to the user.

---

# 📚 Dataset

The project is trained on enterprise financial reports converted into Markdown format to facilitate efficient semantic indexing and retrieval.

**Dataset Source**

https://www.kaggle.com/datasets/rrr3try/enterprise-rag-markdown

The dataset includes:

- Annual Reports
- Quarterly Reports
- SEC Filings
- Financial Statements
- Management Discussions
- Corporate Reports

---

# 🛠️ Technology Stack

## AI & LLM

- LangChain
- LangGraph
- HuggingFace Transformers
- Sentence Transformers

### Models

| Role | Model |
|------|-------|
| **LLM** | `llama-3.3-70b-versatile` via [Groq](https://groq.com) |
| **Embedding** | `BAAI/bge-small-en-v1.5` (local, CPU) via HuggingFace |
| **Reranker** | `cross-encoder/ms-marco-MiniLM-L-6-v2` (local, CPU) via HuggingFace |

## Backend

- FastAPI
- SQLAlchemy
- PostgreSQL
- pgvector
- Alembic
- Redis
- JWT Authentication

## Frontend

- React
- Next.js
- Tailwind CSS

## Deployment

- Docker
- Docker Compose

---

# 📂 Project Structure


---

# ⚙️ Installation

## Clone the Repository

```bash
git clone <repository-url>

cd Agentic_Chatbot_Platform
```

---

## Backend

```bash
cd backend

python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate

pip install -r requirements.txt
```

---

## AI Service

```bash
cd ai

pip install -r requirements.txt
```

---

## Frontend

```bash
cd frontend

npm install
```

---

# ▶️ Running the Project

## Start Backend

```bash
uvicorn app.main:app --reload
```

## Start AI Service

```bash
python main.py
```

## Start Frontend

```bash
npm run dev
```

---

# 🗄️ Database

The platform uses multiple storage layers.

| Component | Purpose |
|-----------|---------|
| PostgreSQL | Relational database for application data |
| pgvector | Vector embeddings and semantic similarity search |
| Redis | Caching, sessions, and application state |

---

# 💬 Example Questions

The chatbot can answer questions such as:

- Summarize Apple's annual financial report.
- What were Microsoft's operating expenses in 2023?
- Compare Amazon's revenue growth over the last three years.
- Identify the major business risks mentioned in Tesla's filings.
- What factors contributed to the decline in net income?
- Explain the company's cash flow position.
- What are the major revenue streams?
- Summarize the management discussion section.
- What acquisitions were completed during the fiscal year?
- Compare quarterly performance with the previous year.

---

# 📈 Use Cases

- Financial Report Summarization
- SEC Filing Analysis
- Enterprise Knowledge Retrieval
- Investment Research Assistance
- Risk Assessment
- Earnings Report Analysis
- Financial Trend Discovery
- Balance Sheet Interpretation
- Cash Flow Analysis
- Business Intelligence

---

# 👥 Team Responsibilities

## Backend

Responsible for:

- Authentication
- JWT Authorization
- Role-Based Access Control (RBAC)
- PostgreSQL Integration
- SQLAlchemy ORM
- Alembic Migrations
- REST APIs
- Redis Integration

---

## AI

Responsible for:

- LangGraph Workflow
- Multi-Agent Orchestration
- Prompt Engineering
- Retrieval-Augmented Generation
- Embedding Generation
- PostgreSQL + pgvector Integration
- Semantic Search
- Context Retrieval
- Response Generation

---

## Frontend

Responsible for:

- Authentication UI
- Dashboard
- Chat Interface
- Document Upload
- Analytics Dashboard
- User Experience

---

# 🚀 Future Improvements

- Citation-aware Responses
- Streaming Responses
- Hybrid Search (BM25 + Vector Search)
- Multi-document Reasoning
- OCR Support for Scanned PDFs
- Financial Chart Generation
- Agent Memory Persistence
- Multi-modal RAG
- Cloud Deployment (AWS / Azure / GCP)
- Human-in-the-Loop Review

---

# 📄 License

This project is intended for educational and research purposes.

---

## ⭐ Acknowledgements

- LangChain
- LangGraph
- FastAPI
- PostgreSQL
- pgvector
- HuggingFace
- React
- Next.js
- Docker

Dataset:
https://www.kaggle.com/datasets/rrr3try/enterprise-rag-markdown
