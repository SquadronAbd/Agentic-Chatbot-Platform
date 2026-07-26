from __future__ import annotations
from typing import Optional

from langchain_core.documents import Document
from loguru import logger


class CrossEncoderReranker:
    """
    Re-ranks candidate documents using a cross-encoder model.
    Gracefully degrades to original ordering when the model is unavailable.
    """

    MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

    def __init__(self, top_k: int = 6) -> None:
        self.top_k = top_k
        self._model = None
        self._load()

    def _load(self) -> None:
        try:
            from sentence_transformers import CrossEncoder
            self._model = CrossEncoder(self.MODEL_NAME)
            logger.info(f"CrossEncoder loaded: {self.MODEL_NAME}")
        except Exception as exc:
            logger.warning(f"CrossEncoder unavailable, re-ranking disabled: {exc}")

    def rerank(self, query: str, documents: list[Document]) -> list[Document]:
        if not documents:
            return documents

        if self._model is None:
            return documents[: self.top_k]

        try:
            pairs = [[query, doc.page_content] for doc in documents]
            scores = self._model.predict(pairs)
            ranked = sorted(zip(scores, documents), key=lambda x: x[0], reverse=True)
            return [doc for _, doc in ranked[: self.top_k]]
        except Exception as exc:
            logger.warning(f"Re-ranking failed, returning original order: {exc}")
            return documents[: self.top_k]


reranker = CrossEncoderReranker()
