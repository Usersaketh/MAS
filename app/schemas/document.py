from pydantic import BaseModel, Field


class DocumentIngestRequest(BaseModel):
    documents: list[str] = Field(..., min_length=1, description="List of knowledge-base documents")


class DocumentIngestResponse(BaseModel):
    added_count: int
    total_documents: int


class RetrieverStatsResponse(BaseModel):
    index_size: int
    metadata_count: int
