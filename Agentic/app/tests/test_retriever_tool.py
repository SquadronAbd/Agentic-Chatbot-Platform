from app.tools.retriever_tool import RetrieverTool

tool = RetrieverTool()

result = tool.search(
    "What company is this report about?"
)

print("=" * 60)
print("Retrieved:", result["count"])
print("=" * 60)

for doc in result["documents"]:

    print(doc.page_content[:300])

    print()

    print(doc.metadata)

    print("-" * 60)