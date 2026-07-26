from app.agents.document_agent import DocumentAgent
from app.memory.conversation import ConversationMemory


agent = DocumentAgent()

memory = ConversationMemory()

result = agent.answer(
    question="What company is this report about?",
    memory=memory,
)

print("=" * 60)
print("ANSWER")
print("=" * 60)
print(result["answer"])

print()

print("=" * 60)
print("DOCUMENTS")
print("=" * 60)
print(len(result["documents"]))

print()

print("=" * 60)
print("SOURCES")
print("=" * 60)

for source in result["sources"]:
    print(source["source"])