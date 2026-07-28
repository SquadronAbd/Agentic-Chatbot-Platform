from typing import Any

from loguru import logger

from app.models.llm import llm
from app.memory.conversation import Message


class ConversationSummarizer:
    """
    Summarizes long conversations.
    """

    def _extract_text(self, response: Any) -> str:

        content = response.content

        if isinstance(content, str):
            return content.strip()

        if isinstance(content, list):
            output = [
                part["text"]
                for part in content
                if isinstance(part, dict) and part.get("text")
            ]
            return "\n".join(output).strip()

        raise ValueError(f"Unexpected LLM response content type: {type(content)}")

    def summarize(
        self,
        history: list[Message],
    ) -> str:

        if not history:
            return ""

        conversation = "\n".join(
            f"{m.role.capitalize()}: {m.content}"
            for m in history
        )

        prompt = (
            "Summarize the conversation.\n\n"
            "Requirements:\n"
            "- Preserve important facts.\n"
            "- Preserve user goals.\n"
            "- Preserve user preferences.\n"
            "- Remove repetition.\n"
            "- Maximum 150 words.\n\n"
            f"Conversation:\n\n{conversation}\n\nSummary:"
        )

        try:
            response = llm.invoke(prompt)
            return self._extract_text(response)
        except Exception as e:
            logger.error(f"Summarization failed: {e}")
            raise