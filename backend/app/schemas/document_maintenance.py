from pydantic import BaseModel


class ChunkIdsRequest(BaseModel):
    chunk_ids: list[str]


class ReindexEmbeddingsResponse(BaseModel):
    requested: int
    chunk_ids: list[str]


class VerifyVectorDeletionResponse(BaseModel):
    verified: list[str]
    pending: list[str]
