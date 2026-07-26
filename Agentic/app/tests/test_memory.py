from app.memory.conversation import ConversationMemory

memory = ConversationMemory()

memory.add_user_message(
    "What is RAG?"
)

memory.add_ai_message(
    "Retrieval-Augmented Generation..."
)

memory.add_user_message(
    "Explain it simply."
)

for message in memory.get_history():

    print(f"{message.role.upper()}:")

    print(message.content)

    print("-" * 40)