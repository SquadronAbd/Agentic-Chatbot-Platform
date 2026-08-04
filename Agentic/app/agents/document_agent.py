import asyncio
from typing import Any, Optional

from app.models.llm import llm
from app.prompts.prompt_builder import PromptBuilder
from app.tools.tool_manager import ToolManager

class DocumentAgent:
    """
    Handles document-based questions using ToolManager.

    Workflow

        Question
            │
            ▼
        ToolManager -> RetrieverTool
            │
            ▼
        Build Prompt
            │
            ▼
           LLM
            │
            ▼
        Return Answer
    """

    def __init__(self, tool_manager: Optional[ToolManager] = None):
        self.tool_manager = tool_manager or ToolManager()
        self.retriever_tool = self.tool_manager.retriever

    def _extract_text(self, response: Any) -> str:
        content = getattr(response, "content", response)

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            output = []
            for part in content:
                if isinstance(part, dict):
                    text = part.get("text")
                    if text:
                        output.append(text)
            return "\n".join(output).strip()

        return str(content)

    async def answer(
        self,
        question: str,
        memory=None,
        source_filter: tuple[str, ...] | None = None,
        owner_id: str | None = None,
    ) -> dict:
        # Retrieval is sync (psycopg + BM25); run in thread to avoid blocking event loop
        search_result = await asyncio.to_thread(
            self.retriever_tool.search, question, source_filter, owner_id
        )
        documents = search_result.get("documents", [])

        history = "" if memory is None else memory.get_history()
        summary = "" if memory is None else memory.get_summary()

        prompt = PromptBuilder.build(
            question=question,
            documents=documents,
            history=history,
            summary=summary,
        )

        response = await llm.ainvoke(prompt)
        answer = self._extract_text(response)

        sources = []
        for doc in documents:
            sources.append(
                {
                    "source": doc.metadata.get(
                        "source",
                        "Unknown",
                    ),
                    "metadata": doc.metadata,
                    "content": doc.page_content,
                }
            )

        return {
            "answer": answer,
            "documents": documents,
            "sources": sources,
        }
