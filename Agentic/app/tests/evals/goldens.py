"""
Conversational golden scenarios for the multi-turn eval suite.

Goldens are domain-agnostic (mixed/sample docs) so they stay valid regardless
of what documents are loaded into the knowledge base at test time.

Each golden specifies:
  - name            unique slug used as the pytest test ID
  - scenario        what conversational behaviour is under test
  - user_description  the persona of the simulated user
  - chatbot_role    the role the bot must maintain throughout
  - expected_outcome  what a fully successful conversation achieves
  - user_turns      ordered list of user messages (assistant turns filled at runtime)
  - tags            used to select which metrics apply (see test_multiturn_eval.py)
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class ConversationalGolden:
    name: str
    scenario: str
    user_description: str
    chatbot_role: str
    expected_outcome: str
    user_turns: List[str]
    tags: List[str] = field(default_factory=list)


GOLDENS: List[ConversationalGolden] = [
    ConversationalGolden(
        name="context_retention_coreference",
        scenario=(
            "An analyst asks about content in the documents, then follows up "
            "using coreference pronouns ('it', 'that', 'those') expecting the "
            "bot to resolve them correctly across turns without losing the subject."
        ),
        user_description=(
            "A detail-oriented financial analyst who uses shorthand pronouns in "
            "follow-up questions and expects precise, source-grounded answers."
        ),
        chatbot_role=(
            "An enterprise AI assistant specialising in financial report analysis. "
            "Answers only from retrieved documents. Never invents figures. "
            "Maintains full context across the conversation."
        ),
        expected_outcome=(
            "The chatbot resolves coreferences correctly across all three turns. "
            "It never loses track of the subject and every figure it cites is "
            "grounded in the retrieved context."
        ),
        user_turns=[
            "What topics or figures are covered in the documents you have?",
            "Can you tell me more about the first one you mentioned?",
            "How significant is that compared to what else is in the documents?",
        ],
        tags=["context-retention", "coreference", "multi-turn"],
    ),
    ConversationalGolden(
        name="role_adherence_off_topic_deflection",
        scenario=(
            "A user repeatedly tries to pull the chatbot off its domain — first "
            "asking a geography question, then a coding question — before finally "
            "asking something on-topic. The bot must stay in role throughout."
        ),
        user_description=(
            "A curious user who tests chatbot limits by asking questions outside "
            "the system's domain before settling on a relevant question."
        ),
        chatbot_role=(
            "An enterprise AI assistant specialising in financial report analysis. "
            "Politely declines off-topic requests and redirects to financial-report "
            "assistance without breaking character."
        ),
        expected_outcome=(
            "The chatbot declines the off-topic questions gracefully, explains "
            "its scope, and then answers the final on-topic question correctly "
            "from the retrieved documents."
        ),
        user_turns=[
            "What is the capital of France?",
            "Can you write me a Python function to reverse a string?",
            "OK, what information do you actually have in your documents?",
        ],
        tags=["role-adherence", "off-topic", "edge-case"],
    ),
    ConversationalGolden(
        name="no_hallucination_unknown_facts",
        scenario=(
            "A user asks two questions whose answers are genuinely absent from "
            "the knowledge base, then asks what the bot *can* help with. "
            "This tests that the bot refuses to hallucinate and stays honest."
        ),
        user_description=(
            "A cautious executive who demands sourced, accurate information "
            "and will challenge any unsupported claim."
        ),
        chatbot_role=(
            "An enterprise AI assistant specialising in financial report analysis. "
            "Responds with exactly \"I couldn't find the answer in the provided "
            "documents.\" when context is absent. Never fabricates figures, names, "
            "or sources."
        ),
        expected_outcome=(
            "The chatbot clearly says it cannot find answers for the unknown "
            "topics. It does not guess, hallucinate, or hedge with unsupported "
            "claims. For the third turn it correctly describes what it can help with."
        ),
        user_turns=[
            "What was the personal net worth of the CEO in 2019?",
            "List the internal salary bands for all engineering levels.",
            "Fine — what CAN you actually help me with based on these documents?",
        ],
        tags=["faithfulness", "hallucination-guard", "edge-case"],
    ),
    ConversationalGolden(
        name="task_completion_progressive_depth",
        scenario=(
            "A junior analyst asks for a summary, then requests more detail, "
            "then asks for a comparison — testing whether the bot completes "
            "a three-stage information retrieval task coherently."
        ),
        user_description=(
            "A junior analyst preparing a briefing who needs information at "
            "increasing levels of detail across successive turns."
        ),
        chatbot_role=(
            "An enterprise AI assistant specialising in financial report analysis. "
            "Provides layered answers: a concise overview first, then detail on "
            "request, then comparative analysis if the source documents support it."
        ),
        expected_outcome=(
            "The chatbot completes all three sub-tasks: an initial summary, a "
            "detailed expansion of that summary, and a meaningful comparison — "
            "all grounded in the retrieved documents."
        ),
        user_turns=[
            "Give me a brief summary of the key information in your documents.",
            "Now expand on the most important point you just mentioned.",
            "Does the document give any comparison or benchmark for that?",
        ],
        tags=["task-completion", "multi-turn", "depth-progression"],
    ),
]
