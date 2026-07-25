from app.models.vector_store import vector_store

print("=" * 50)
print("Chroma Collection Information")
print("=" * 50)

collection = vector_store._collection

print(f"Collection Name : {collection.name}")
print(f"Total Documents : {collection.count()}")