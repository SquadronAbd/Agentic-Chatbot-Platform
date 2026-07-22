---

# 3. AI `README.md`

**Location**

```text
ai/
README.md
```

```md
# AI Service

This module implements the Multi-Agent RAG system.

---

## Technologies

- LangChain
- LangGraph
- OpenAI
- Qdrant
- Sentence Transformers
- BM25
- PyTorch

---

## Install

Create virtual environment

```bash
python -m venv .venv
```

Activate

Windows

```bash
.venv\Scripts\activate
```

Linux/Mac

```bash
source .venv/bin/activate
```

Install packages

```bash
pip install -r requirements.txt
```

---

## Folder Structure

```text
ai/
│
├── agents/
├── rag/
├── vector_store/
├── workflows/
├── prompts/
├── evaluation/
├── requirements.txt
└── README.md
```

---

## Responsibilities

- Document Chunking
- Embedding Generation
- Qdrant Indexing
- Retrieval
- Agent Routing
- Response Generation
- Prompt Engineering
- Multi-Agent Workflow

---

## Notes

This module communicates with the FastAPI backend via APIs.

It does not directly expose database endpoints.
```

---