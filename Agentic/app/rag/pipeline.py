from pathlib import Path
from loguru import logger

from app.rag.loader import DocumentLoader
from app.rag.cleaner import DocumentCleaner
from app.rag.chunker import DocumentChunker
from app.models.vector_store import vector_store
from app.rag.bm25_corpus import bm25_corpus


class Pipeline:

    def __init__(self):

        self.loader = DocumentLoader()
        self.cleaner = DocumentCleaner()
        self.chunker = DocumentChunker()

    # ----------------------------
    # Single File
    # ----------------------------

    def ingest(self, filepath: str):

        logger.info(f"Loading {filepath}")

        documents = self.loader.load(filepath)

        documents = self.cleaner.clean(documents)

        chunks = self.chunker.chunk(documents)

        logger.info(f"Adding {len(chunks)} chunks")

        vector_store.add_documents(chunks)
        bm25_corpus.add(chunks)

        return len(chunks)

    # ----------------------------
    # Entire Folder
    # ----------------------------

    def ingest_directory(self, folder: str):

        folder = Path(folder)

        total_files = 0
        total_chunks = 0

        for file in folder.rglob("*.md"):

            logger.info(f"Ingesting {file.name}")

            count = self.ingest(str(file))

            total_files += 1
            total_chunks += count

        logger.success(
            f"Indexed {total_files} files ({total_chunks} chunks)"
        )

        return total_files, total_chunks


pipeline = Pipeline()