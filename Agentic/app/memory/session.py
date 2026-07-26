from app.memory.conversation import ConversationMemory


class SessionManager:
    """
    Manages conversation memories for multiple users/sessions.
    """

    def __init__(self):
        # Dictionary:
        # key   -> session_id
        # value -> ConversationMemory
        self.sessions: dict[str, ConversationMemory] = {}

    def create_session(self, session_id: str) -> ConversationMemory:
        """
        Create a new session if it doesn't exist.
        """

        if session_id not in self.sessions:
            self.sessions[session_id] = ConversationMemory()

        return self.sessions[session_id]

    def get_memory(self, session_id: str) -> ConversationMemory:
        """
        Return the conversation memory for a session.
        """

        if session_id not in self.sessions:
            return self.create_session(session_id)

        return self.sessions[session_id]

    def delete_session(self, session_id: str) -> bool:
        """
        Delete a session.

        Returns True if deleted, False otherwise.
        """

        if session_id in self.sessions:
            del self.sessions[session_id]
            return True

        return False

    def clear_session(self, session_id: str) -> bool:
        """
        Clear conversation history without deleting the session.
        """

        if session_id in self.sessions:
            self.sessions[session_id].clear()
            return True

        return False

    def list_sessions(self) -> list[str]:
        """
        Return all active session IDs.
        """

        return list(self.sessions.keys())

    def session_exists(self, session_id: str) -> bool:
        """
        Check whether a session exists.
        """

        return session_id in self.sessions

    def total_sessions(self) -> int:
        """
        Return total number of active sessions.
        """

        return len(self.sessions)


# Module-level singleton — import this everywhere instead of instantiating SessionManager()
session_manager = SessionManager()