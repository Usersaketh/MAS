from fastapi import APIRouter

from app.schemas.query import ConversationTurn, TraceEvent
from app.services.runtime import memory_service, trace_service

router = APIRouter(prefix="/observability", tags=["observability"])


@router.get("/conversations/{conversation_id}/memory", response_model=list[ConversationTurn])
def get_conversation_memory(conversation_id: str) -> list[ConversationTurn]:
    return memory_service.get_recent_turns(conversation_id)


@router.get("/conversations/{conversation_id}/traces", response_model=list[TraceEvent])
def get_conversation_traces(conversation_id: str) -> list[TraceEvent]:
    return trace_service.get_latest(conversation_id)
