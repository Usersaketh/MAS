from fastapi import APIRouter, Depends
import logging

from app.schemas.document import DocumentIngestRequest, DocumentIngestResponse, RetrieverStatsResponse
from app.services.security import enforce_request_security
from app.services.runtime import retriever

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/documents", tags=["documents"], dependencies=[Depends(enforce_request_security)])


@router.post("", response_model=DocumentIngestResponse)
def ingest_documents(payload: DocumentIngestRequest) -> DocumentIngestResponse:
    try:
        before = len(retriever.documents)
        retriever.add_documents(payload.documents)
        after = len(retriever.documents)

        return DocumentIngestResponse(
            added_count=after - before,
            total_documents=after,
        )
    except Exception as e:
        logger.error(f"Error ingesting documents: {str(e)}", exc_info=True)
        raise


@router.get("/stats", response_model=RetrieverStatsResponse)
def retriever_stats() -> RetrieverStatsResponse:
    stats = retriever.stats()
    return RetrieverStatsResponse(**stats)
