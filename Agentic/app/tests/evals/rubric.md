# Eval Rubric — Financial RAG Agent

## System under test

- **Name**: Agentic Financial RAG Assistant
- **Input type**: Multi-turn conversation (`session_id` + `question`)
- **Output type**: Single response + retrieved source chunks (`answer` + `sources[]`)
- **Deployment context**: Internal dev tool — regression tracking, moderate rigour
- **Entry point**: `POST /chat` → `RAGService.ask()` → LangGraph graph → DocumentAgent / PlannerAgent / GeneralAgent → ReflectionAgent

## Criteria

### Criterion 1: Faithfulness

- **Definition**: Every factual claim in the answer is directly supported by at least one of the retrieved source chunks. The judge checks that no figure, percentage, date, name, or assertion appears in the answer without a matching passage in the provided context.
- **Level**: `trajectory`
- **Scoring**: `3-point`
- **Scale anchors**:
  - `pass (2)`: All claims are explicitly grounded in the retrieved context. The judge can point to specific text for each claim.
  - `partial (1)`: Most claims are grounded but one or two minor claims are inferred rather than directly stated (e.g. arithmetic from figures that are present). No invented figures.
  - `fail (0)`: One or more material claims (figures, names, dates, conclusions) have no basis in the retrieved context, or the answer contradicts the context.
- **Failure modes caught**:
  - Hallucinated financial figures not present in any retrieved chunk
  - Fabricated source citations ("According to the 2023 Annual Report..." when that document wasn't retrieved)
  - Correct claim but from a chunk that was NOT in the retrieval set (judge cannot verify)
  - Answer contradicts a retrieved chunk
- **Bias risks**:
  - *Distraction bias*: retrieved chunks can be long; the judge may miss an unsupported claim buried in a long answer. Mitigation: instruct judge to check each claim individually, not holistically.
  - *Verbosity bias*: longer answers may appear more thorough and grounded. Mitigation: explicit instruction to score based on verification, not length.
- **Aggregation weight**: 0.45 (highest priority)

---

### Criterion 2: Refusal Correctness

- **Definition**: When the answer to the user's question is absent from the retrieved context, the agent must respond with the exact phrase "I couldn't find the answer in the provided documents." and nothing more. When the answer IS in the context, the agent must NOT refuse.
- **Level**: `trajectory`
- **Scoring**: `binary`
- **Scale anchors**:
  - `pass (1)`: Correct behaviour in both directions — refuses when it should, answers when it should. The refusal uses the exact prescribed phrase (or a close paraphrase that conveys the same meaning without adding unsupported content).
  - `fail (0)`: Any of: (a) agent answers confidently when context contains no relevant information; (b) agent refuses or heavily hedges when the answer IS in the context; (c) agent produces a partial answer while signalling uncertainty, effectively hallucinating.
- **Failure modes caught**:
  - Confidently wrong answer when context is empty
  - Over-refusal ("I cannot answer financial questions") when context is present
  - Hedged hallucination ("Based on general knowledge, revenue is typically...")
  - Mixing a correct refusal with unsupported speculation
- **Bias risks**:
  - *Refusal/uncertainty bias*: judges tend to rate ambiguous cases as partial — not applicable here since this is binary. Force the judge to pick a side.
  - *Sycophancy on reference*: if the judge is given the expected phrase verbatim, it may over-penalise paraphrases. Mitigation: describe acceptable paraphrases explicitly.
- **Aggregation weight**: 0.30

---

### Criterion 3: Task Completion

- **Definition**: The agent's response fully addresses everything the user asked. All sub-questions are answered, requested comparisons are made, and no part of a compound question is dropped.
- **Level**: `trajectory`
- **Scoring**: `3-point`
- **Scale anchors**:
  - `pass (2)`: Every element of the user's question is addressed. For multi-part questions, all parts receive a substantive answer (not just an acknowledgment).
  - `partial (1)`: The main question is answered but one or more secondary parts are missing or answered superficially. The answer is still useful.
  - `fail (0)`: The agent fails to answer the primary question, goes off-topic, or answers a different question than what was asked.
- **Failure modes caught**:
  - Dropped sub-questions in compound queries ("What was Q3 revenue, and how does that compare to Q2?")
  - Off-topic answer (intent misclassified, agent answers a different question)
  - Partial answer presented as complete (e.g. gives revenue but ignores the requested comparison)
  - Reflection agent stripping content that was needed to answer the question
- **Bias risks**:
  - *Verbosity bias*: longer answers appear more complete. Mitigation: require the judge to list each part of the question and check it individually.
  - *Halo bias*: a well-formatted answer may seem complete even when content is missing. Mitigation: anchor on substance, not presentation.
- **Aggregation weight**: 0.25

---

## Aggregation

**Mode**: `weighted average`

Weights: Faithfulness 0.45 · Refusal Correctness 0.30 · Task Completion 0.25

Normalise each criterion to [0, 1] before weighting (3-point: divide by 2; binary: already 0/1).

**Regression threshold**: overall score ≥ 0.70 to pass. Flag any individual criterion below 0.50.

Refusal Correctness is **sticky-fail**: a `fail` on this criterion always surfaces in the report regardless of the aggregate score, because confidently wrong answers are the highest-risk failure mode for a financial system.
