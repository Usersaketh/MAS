from fastapi.testclient import TestClient

from app.main import app
from app.api.routes import query as query_route


class FakeGraph:
    def run(self, conversation_id: str, query: str):
        return {
            "answer": "mock answer",
            "agent_trace": ["retriever_agent", "memory_recall", "intent_classifier"],
            "retrieved_context": ["context 1"],
            "recent_turns": [],
            "trace_events": [],
            "intent": "general",
            "confidence": 0.8,
            "needs_escalation": False,
            "escalation_reason": None,
            "policy_violations": [],
        }


def test_query_route_returns_stage4_fields(monkeypatch):
    monkeypatch.setattr(query_route, "agent_graph", FakeGraph())

    client = TestClient(app)
    response = client.post(
        "/query",
        json={"user_id": "u1", "conversation_id": "conv-a", "query": "Hello"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["conversation_id"] == "conv-a"
    assert payload["answer"] == "mock answer"
    assert payload["intent"] == "general"
    assert payload["confidence"] == 0.8
    assert payload["needs_escalation"] is False
