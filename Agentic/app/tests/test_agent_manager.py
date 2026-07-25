from app.agents.agent_manager import AgentManager
from app.memory.conversation import ConversationMemory

manager = AgentManager()

memory = ConversationMemory()

result = manager.ask(
    question="What company is this report about?",
    memory=memory,
)

print(result["answer"])