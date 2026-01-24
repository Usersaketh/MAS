from __future__ import annotations

from datetime import datetime, timezone
from time import perf_counter
from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph

from app.schemas.query import ConversationTurn, TraceEvent
from app.services.llm_service import OllamaService
from app.services.memory_service import ConversationMemoryService
from app.services.retriever_service import RetrieverService
from app.services.stage3_agents import EscalationEvaluatorAgent, IntentClassifierAgent, PolicyGuardrailsAgent
from app.services.trace_service import TraceRun, TraceService


class AgentState(TypedDict):
    conversation_id: str
    query: str
    recent_turns: list[ConversationTurn]
    retrieved_context: list[str]
    intent: str
    confidence: float
    needs_escalation: bool
    escalation_reason: str | None
    policy_violations: list[str]
    answer: str
    agent_trace: list[str]
    trace_id: str
    trace_events: list[TraceEvent]


class QueryAgentGraph:
    def __init__(
        self,
        retriever: RetrieverService,
        llm: OllamaService,
        memory_service: ConversationMemoryService,
        trace_service: TraceService,
    ) -> None:
        self.retriever = retriever
        self.llm = llm
        self.memory_service = memory_service
        self.trace_service = trace_service
        self.intent_classifier = IntentClassifierAgent(llm)
        self.escalation_evaluator = EscalationEvaluatorAgent(llm)
        self.policy_guardrails = PolicyGuardrailsAgent(llm)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(AgentState)

        graph_builder.add_node("retriever_agent", self._retriever_step)
        graph_builder.add_node("memory_recall", self._memory_recall_step)
        graph_builder.add_node("intent_classifier", self._intent_classifier_step)
        graph_builder.add_node("escalation_evaluator", self._escalation_evaluator_step)
        graph_builder.add_node("policy_guardrails", self._policy_guardrails_step)
        graph_builder.add_node("reasoning_agent", self._reasoning_step)

        graph_builder.set_entry_point("retriever_agent")
        graph_builder.add_edge("retriever_agent", "memory_recall")
        graph_builder.add_edge("memory_recall", "intent_classifier")
        graph_builder.add_edge("intent_classifier", "escalation_evaluator")
        graph_builder.add_conditional_edges(
            "escalation_evaluator",
            self._route_on_escalation,
            {
                "escalated": END,
                "policy_check": "policy_guardrails",
            },
        )
        graph_builder.add_edge("policy_guardrails", "reasoning_agent")
        graph_builder.add_edge("reasoning_agent", END)

        return graph_builder.compile()

    def _route_on_escalation(self, state: AgentState) -> Literal["escalated", "policy_check"]:
        if state["needs_escalation"]:
            return "escalated"
        return "policy_check"

    def _retriever_step(self, state: AgentState) -> AgentState:
        started_at = perf_counter()
        context = self.retriever.search(state["query"], top_k=3)
        trace = state.get("agent_trace", []) + ["retriever_agent"]
        trace_events = list(state.get("trace_events", []))
        trace_events.append(
            TraceEvent(
                step="retriever_agent",
                status="completed",
                timestamp=datetime.now(timezone.utc).isoformat(),
                duration_ms=(perf_counter() - started_at) * 1000,
                message=f"Retrieved {len(context)} context chunks",
            )
        )
        return {**state, "retrieved_context": context, "agent_trace": trace, "trace_events": trace_events}

    def _memory_recall_step(self, state: AgentState) -> AgentState:
        started_at = perf_counter()
        recent_turns = self.memory_service.get_recent_turns(state["conversation_id"])
        trace = state.get("agent_trace", []) + ["memory_recall"]
        trace_events = list(state.get("trace_events", []))
        trace_events.append(
            TraceEvent(
                step="memory_recall",
                status="completed",
                timestamp=datetime.now(timezone.utc).isoformat(),
                duration_ms=(perf_counter() - started_at) * 1000,
                message=f"Loaded {len(recent_turns)} recent turns",
            )
        )
        return {**state, "recent_turns": recent_turns, "agent_trace": trace, "trace_events": trace_events}

    def _intent_classifier_step(self, state: AgentState) -> AgentState:
        started_at = perf_counter()
        classification = self.intent_classifier.classify(state["query"])
        trace = state.get("agent_trace", []) + ["intent_classifier"]
        trace_events = list(state.get("trace_events", []))
        trace_events.append(
            TraceEvent(
                step="intent_classifier",
                status="completed",
                timestamp=datetime.now(timezone.utc).isoformat(),
                duration_ms=(perf_counter() - started_at) * 1000,
                message=f"Intent={classification.intent} confidence={classification.confidence:.2f}",
            )
        )
        return {
            **state,
            "intent": classification.intent,
            "confidence": classification.confidence,
            "agent_trace": trace,
            "trace_events": trace_events,
        }

    def _escalation_evaluator_step(self, state: AgentState) -> AgentState:
        started_at = perf_counter()
        decision = self.escalation_evaluator.evaluate(
            state["query"],
            state["intent"],
            state["confidence"],
            state.get("retrieved_context", []),
        )
        trace = state.get("agent_trace", []) + ["escalation_evaluator"]
        trace_events = list(state.get("trace_events", []))
        trace_events.append(
            TraceEvent(
                step="escalation_evaluator",
                status="completed",
                timestamp=datetime.now(timezone.utc).isoformat(),
                duration_ms=(perf_counter() - started_at) * 1000,
                message=f"Escalation={decision.needs_escalation} reason={decision.reason}",
            )
        )
        return {
            **state,
            "needs_escalation": decision.needs_escalation,
            "escalation_reason": decision.reason if decision.needs_escalation else None,
            "answer": (
                "Your request has been escalated to a human support agent. "
                f"Reason: {decision.reason}"
                if decision.needs_escalation
                else state.get("answer", "")
            ),
            "agent_trace": trace,
            "trace_events": trace_events,
        }

    def _policy_guardrails_step(self, state: AgentState) -> AgentState:
        started_at = perf_counter()
        check_result = self.policy_guardrails.check(state["query"], state["intent"])
        trace = state.get("agent_trace", []) + ["policy_guardrails"]
        trace_events = list(state.get("trace_events", []))
        trace_events.append(
            TraceEvent(
                step="policy_guardrails",
                status="completed",
                timestamp=datetime.now(timezone.utc).isoformat(),
                duration_ms=(perf_counter() - started_at) * 1000,
                message=f"Policy pass={check_result.passes_policy} violations={len(check_result.violations)}",
            )
        )
        return {
            **state,
            "policy_violations": check_result.violations,
            "agent_trace": trace,
            "trace_events": trace_events,
        }

    def _reasoning_step(self, state: AgentState) -> AgentState:
        started_at = perf_counter()
        context = "\n".join(state.get("retrieved_context", []))
        intent = state.get("intent", "general")
        recent_turns = state.get("recent_turns", [])

        intent_prompts = {
            "billing": "You are a billing support specialist. Be precise about fees, charges, and payment terms.\n",
            "shipping": "You are a shipping support specialist. Provide accurate timelines and tracking information.\n",
            "account": "You are an account support specialist. Focus on security, privacy, and account management.\n",
            "complaint": "You are a complaints handler. Show empathy and work toward resolution.\n",
            "general": "You are a customer support assistant.\n",
        }

        intent_prompt = intent_prompts.get(intent, intent_prompts["general"])
        policy_note = ""
        if state.get("policy_violations"):
            policy_note = "\nIMPORTANT POLICY NOTES:\n" + "\n".join(state["policy_violations"]) + "\n"

        memory_note = ""
        if recent_turns:
            formatted_turns = []
            for turn in recent_turns:
                formatted_turns.append(f"{turn.role.upper()}: {turn.content}")
            memory_note = "\nRECENT CONVERSATION:\n" + "\n".join(formatted_turns) + "\n"

        prompt = (
            f"{intent_prompt}"
            f"Use the context when relevant.\n\n"
            f"Context:\n{context or 'No relevant context found.'}\n\n"
            f"{memory_note}"
            f"{policy_note}"
            f"Customer Query:\n{state['query']}\n\n"
            "Provide a concise and helpful answer."
        )

        answer = self.llm.generate(prompt)
        trace = state.get("agent_trace", []) + ["reasoning_agent"]
        trace_events = list(state.get("trace_events", []))
        trace_events.append(
            TraceEvent(
                step="reasoning_agent",
                status="completed",
                timestamp=datetime.now(timezone.utc).isoformat(),
                duration_ms=(perf_counter() - started_at) * 1000,
                message="Generated final response",
            )
        )
        return {**state, "answer": answer, "agent_trace": trace, "trace_events": trace_events}

    def run(self, conversation_id: str, query: str) -> AgentState:
        trace_run: TraceRun = self.trace_service.begin_run(conversation_id)
        initial_state: AgentState = {
            "conversation_id": conversation_id,
            "query": query,
            "recent_turns": [],
            "retrieved_context": [],
            "intent": "general",
            "confidence": 0.0,
            "needs_escalation": False,
            "escalation_reason": None,
            "policy_violations": [],
            "answer": "",
            "agent_trace": [],
            "trace_id": trace_run.trace_id,
            "trace_events": [],
        }
        result = self.graph.invoke(initial_state)
        trace_run.events = result.get("trace_events", [])
        self.trace_service.finish_run(trace_run)
        self.memory_service.append_turn(conversation_id, query, result["answer"], result.get("intent", "general"))
        return result
