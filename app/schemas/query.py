from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    user_id: str = Field(..., description="Unique identifier for the customer")
    query: str = Field(..., min_length=2, description="Customer query text")


class QueryResponse(BaseModel):
    answer: str
    agent_trace: list[str]
    retrieved_context: list[str]
