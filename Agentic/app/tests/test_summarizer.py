from app.memory.conversation import ConversationMemory
from app.memory.summarizer import ConversationSummarizer

memory = ConversationMemory()

memory.add_user_message("What is RAG?")
memory.add_ai_message(
    "RAG combines vector search with language models."
)

memory.add_user_message("Explain it simply.")
memory.add_ai_message(
    "It searches documents before generating an answer."
)

memory.add_user_message("What is LangGraph?")
memory.add_ai_message(
    "LangGraph helps build stateful AI workflows."
)

summarizer = ConversationSummarizer()

summary = summarizer.summarize(
    memory.get_history()
)

print("=" * 60)
print("SUMMARY")
print("=" * 60)
print(summary)