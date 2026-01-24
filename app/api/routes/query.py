from fastapi import APIRouter, Depends

from app.schemas.query import QueryRequest, QueryResponse
from app.services.security import enforce_request_security
from app.services.runtime import agent_graph, retriever

router = APIRouter(prefix="/query", tags=["query"], dependencies=[Depends(enforce_request_security)])


@router.post("", response_model=QueryResponse)
def process_query(payload: QueryRequest) -> QueryResponse:
    conversation_id = payload.conversation_id or payload.user_id
    result = agent_graph.run(conversation_id, payload.query)
    return QueryResponse(
        conversation_id=conversation_id,
        answer=result["answer"],
        agent_trace=result["agent_trace"],
        retrieved_context=result["retrieved_context"],
        recent_turns=result["recent_turns"],
        trace_events=result["trace_events"],
        intent=result["intent"],
        confidence=result["confidence"],
        needs_escalation=result["needs_escalation"],
        escalation_reason=result["escalation_reason"],
        policy_violations=result["policy_violations"],
    )
