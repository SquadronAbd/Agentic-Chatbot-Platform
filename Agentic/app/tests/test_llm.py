from app.models.llm import llm

response = llm.invoke(
    "Explain Retrieval-Augmented Generation in one sentence."
)

print(response.content)