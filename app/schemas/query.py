from pydantic import BaseModel, Field


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
    query: str = Field(..., min_length=2, description="Customer query text")


class QueryResponse(BaseModel):
    answer: str
    agent_trace: list[str]
    retrieved_context: list[str]
    intent: str
    confidence: float
    needs_escalation: bool
    escalation_reason: str | None
    policy_violations: list[str]
