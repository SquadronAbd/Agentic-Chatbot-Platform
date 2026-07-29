from app.agents.general_agent import GeneralAgent
from app.memory.conversation import ConversationMemory

memory = ConversationMemory()
memory.add_user_message("My name is Abdullah.")
memory.add_ai_message("Nice to meet you.")

agent = GeneralAgent()

answer = agent.answer(
    question="What is my name?",
    memory=memory,
)

print(answer)
