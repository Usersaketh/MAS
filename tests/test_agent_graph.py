from app.services.agent_graph import QueryAgentGraph
from app.services.memory_service import ConversationMemoryService
from app.services.trace_service import TraceService


class FakeRetriever:
    def search(self, query: str, top_k: int = 3):
        if "package" in query.lower():
            return ["Shipping usually takes 3-5 business days for domestic orders."]
        return ["Refund requests are processed within 7 business days after approval."]


class FakeLLM:
    def generate(self, prompt: str) -> str:
        lower_prompt = prompt.lower()
        if "classify the customer query" in lower_prompt:
            if "refund" in lower_prompt or "angry" in lower_prompt:
                return "INTENT: billing, CONFIDENCE: 0.41"
            if "package" in lower_prompt or "shipping" in lower_prompt:
                return "INTENT: shipping, CONFIDENCE: 0.93"
            return "INTENT: general, CONFIDENCE: 0.74"

        return "Test answer from fake llm."


def build_graph(tmp_path):
    memory_service = ConversationMemoryService(memory_path=str(tmp_path / "memory.json"), max_turns=4)
    trace_service = TraceService(trace_path=str(tmp_path / "traces.json"))
    return QueryAgentGraph(
        retriever=FakeRetriever(),
        llm=FakeLLM(),
        memory_service=memory_service,
        trace_service=trace_service,
    ), memory_service, trace_service


def test_graph_runs_with_memory_and_trace(tmp_path):
    graph, memory_service, trace_service = build_graph(tmp_path)

    first_result = graph.run("conv-1", "Where is my package?")

    assert first_result["intent"] == "shipping"
    assert first_result["needs_escalation"] is False
    assert first_result["answer"] == "Test answer from fake llm."
    assert "reasoning_agent" in first_result["agent_trace"]
    assert len(first_result["trace_events"]) == 6

    memory_after_first_run = memory_service.get_recent_turns("conv-1")
    assert len(memory_after_first_run) == 2

    second_result = graph.run("conv-1", "Can I refund my order?")

    assert second_result["intent"] == "billing"
    assert len(second_result["recent_turns"]) == 2
    assert second_result["trace_id"]
    assert trace_service.get_latest("conv-1")


def test_graph_returns_handoff_message_when_escalated(tmp_path):
    graph, _, _ = build_graph(tmp_path)

    result = graph.run("conv-2", "I am angry and want a refund now!")

    assert result["needs_escalation"] is True
    assert result["answer"].startswith("Your request has been escalated to a human support agent.")
    assert "reasoning_agent" not in result["agent_trace"]
    assert len(result["trace_events"]) == 4
