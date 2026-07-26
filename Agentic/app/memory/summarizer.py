from typing import Any

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

            output = []

            for part in content:

                if isinstance(part, dict):

                    text = part.get("text")

                    if text:
                        output.append(text)

            return "\n".join(output).strip()

        return str(content)

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

        prompt = f"""
Summarize the conversation.

Requirements:

- Preserve important facts.
- Preserve user goals.
- Preserve user preferences.
- Remove repetition.
- Maximum 150 words.

Conversation:

{conversation}

Summary:
"""

        response = llm.invoke(prompt)

        return self._extract_text(response)