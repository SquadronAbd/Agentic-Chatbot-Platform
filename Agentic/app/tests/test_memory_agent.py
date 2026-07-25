from app.agents.memory_agent import MemoryAgent
from app.memory.conversation import ConversationMemory

memory = ConversationMemory()

memory.add_user_message("My name is Abdullah.")
memory.add_ai_message("Nice to meet you.")

agent = MemoryAgent()

answer = agent.answer(
    question="What is my name?",
    memory=memory,
)

print(answer)