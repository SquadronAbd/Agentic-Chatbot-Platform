from app.rag.pipeline import RAGPipeline

pipeline = RAGPipeline()

count = pipeline.ingest("documents/sample.txt")

print()

print(f"Stored {count} chunks.")