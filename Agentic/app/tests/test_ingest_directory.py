from app.rag.pipeline import pipeline

files, chunks = pipeline.ingest_directory(
    "documents/financial_reports"
)

print("=" * 60)
print("FILES INDEXED")
print("=" * 60)
print(files)

print()

print("=" * 60)
print("TOTAL CHUNKS")
print("=" * 60)
print(chunks)