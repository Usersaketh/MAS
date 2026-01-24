from pydantic import BaseModel, Field


class ConversationTurn(BaseModel):
    role: str
    content: str
    intent: str | None = None
    timestamp: str


class TraceEvent(BaseModel):
    step: str
    status: str
    timestamp: str
    duration_ms: float | None = None
    message: str | None = None


class IntentClassification(BaseModel):
    intent: str = Field(..., description="Classified intent (billing, shipping, account, complaint, general)")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")


class EscalationDecision(BaseModel):
    needs_escalation: bool
    reason: str


class PolicyCheckResult(BaseModel):
    passes_policy: bool
    violations: list[str]
    notes: str


class QueryRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the customer")
    conversation_id: str | None = Field(default=None, description="Conversation identifier for memory tracking")
    query: str = Field(..., min_length=2, description="Customer query text")


class QueryResponse(BaseModel):
    conversation_id: str
    answer: str
    agent_trace: list[str]
    retrieved_context: list[str]
    recent_turns: list[ConversationTurn]
    trace_events: list[TraceEvent]
    intent: str
    confidence: float
    needs_escalation: bool
    escalation_reason: str | None
    policy_violations: list[str]
