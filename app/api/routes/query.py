from fastapi import APIRouter

from app.schemas.query import QueryRequest, QueryResponse
from app.services.runtime import agent_graph, retriever

router = APIRouter(prefix="/query", tags=["query"])

# Seed a tiny in-memory corpus for Stage 1 demonstration.
if retriever.index.ntotal == 0:
    retriever.add_documents(
        [
            "Shipping usually takes 3-5 business days for domestic orders.",
            "Refund requests are processed within 7 business days after approval.",
            "You can reset your password from the account settings page.",
        ]
    )


@router.post("", response_model=QueryResponse)
def process_query(payload: QueryRequest) -> QueryResponse:
    result = agent_graph.run(payload.query)
    return QueryResponse(
        answer=result["answer"],
        agent_trace=result["agent_trace"],
        retrieved_context=result["retrieved_context"],
    )
