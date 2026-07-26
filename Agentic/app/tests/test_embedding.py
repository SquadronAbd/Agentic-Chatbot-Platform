from app.models.embeddings import embeddings

vector = embeddings.embed_query("What is Artificial Intelligence?")

print("=" * 60)
print("Embedding length")
print("=" * 60)

print(len(vector))