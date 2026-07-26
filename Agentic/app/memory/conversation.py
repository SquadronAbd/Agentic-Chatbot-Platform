from dataclasses import dataclass
from typing import List


@dataclass
class Message:
    role: str
    content: str


class ConversationMemory:
    """
    Stores conversation history for a single session.

    Features:
    - User/Assistant messages
    - Conversation summary
    - Recent message retrieval
    - Automatic replacement after summarization
    """

    def __init__(self):

        self.messages: List[Message] = []

        self.summary: str = ""

    # ----------------------------------------------------
    # Add Messages
    # ----------------------------------------------------

    def add_user_message(self, content: str):

        self.messages.append(
            Message(
                role="user",
                content=content,
            )
        )

    def add_ai_message(self, content: str):

        self.messages.append(
            Message(
                role="assistant",
                content=content,
            )
        )

    # ----------------------------------------------------
    # Conversation
    # ----------------------------------------------------

    def get_history(self) -> list[Message]:

        return self.messages

    def clear(self):

        self.messages.clear()

        self.summary = ""

    # ----------------------------------------------------
    # Summary
    # ----------------------------------------------------

    def set_summary(self, summary: str):

        self.summary = summary

    def get_summary(self) -> str:

        return self.summary

    # ----------------------------------------------------
    # Helpers
    # ----------------------------------------------------

    def message_count(self) -> int:

        return len(self.messages)

    def last_messages(self, n: int = 6) -> list[Message]:

        return self.messages[-n:]

    def replace_history(
        self,
        summary: str,
        recent_messages: list[Message],
    ):
        """
        Replace the old conversation with:

        - Conversation summary
        - Last N messages
        """

        self.summary = summary

        self.messages = list(recent_messages)