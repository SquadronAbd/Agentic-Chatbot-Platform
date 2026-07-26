from app.memory.conversation import ConversationMemory


class MemoryService:

    def answer(
        self,
        question: str,
        memory: ConversationMemory,
    ) -> str:

        question = question.lower()

        if "summary" in question:

            if memory.get_summary():

                return memory.get_summary()

            history = memory.get_history()

            if not history:

                return "No conversation yet."

            return "\n".join(

                f"{m.role}: {m.content}"

                for m in history

            )

        if "who are we talking about" in question:

            if memory.get_summary():

                return memory.get_summary()

            return "We are discussing the current conversation."

        if "what did i ask" in question:

            history = memory.get_history()

            users = [

                m.content

                for m in history

                if m.role == "user"

            ]

            if not users:

                return "You haven't asked anything yet."

            return users[-1]

        return "I couldn't answer from conversation memory."