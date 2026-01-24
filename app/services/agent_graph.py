from __future__ import annotations

from typing import Literal, TypedDict

from langgraph.graph import END, StateGraph

from app.core.config import settings
from app.services.llm_service import OllamaService
from app.services.retriever_service import RetrieverService
from app.services.stage3_agents import EscalationEvaluatorAgent, IntentClassifierAgent, PolicyGuardrailsAgent


class AgentState(TypedDict):
    query: str
    retrieved_context: list[str]
    intent: str
    confidence: float
    needs_escalation: bool
    escalation_reason: str | None
    policy_violations: list[str]
    answer: str
    agent_trace: list[str]


class QueryAgentGraph:
    def __init__(self, retriever: RetrieverService, llm: OllamaService) -> None:
        self.retriever = retriever
        self.llm = llm
        self.intent_classifier = IntentClassifierAgent(llm)
        self.escalation_evaluator = EscalationEvaluatorAgent(llm)
        self.policy_guardrails = PolicyGuardrailsAgent(llm)
        self.graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(AgentState)

        # Node definitions
        graph_builder.add_node("retriever_agent", self._retriever_step)
        graph_builder.add_node("intent_classifier", self._intent_classifier_step)
        graph_builder.add_node("escalation_evaluator", self._escalation_evaluator_step)
        graph_builder.add_node("policy_guardrails", self._policy_guardrails_step)
        graph_builder.add_node("reasoning_agent", self._reasoning_step)

        # Entry point and flow
        graph_builder.set_entry_point("retriever_agent")

        # retriever -> intent_classifier -> escalation_evaluator
        graph_builder.add_edge("retriever_agent", "intent_classifier")
        graph_builder.add_edge("intent_classifier", "escalation_evaluator")

        # Conditional routing after escalation evaluation
        graph_builder.add_conditional_edges(
            "escalation_evaluator",
            self._route_on_escalation,
            {
                "escalated": END,
                "policy_check": "policy_guardrails",
            },
        )

        # policy_guardrails -> reasoning_agent
        graph_builder.add_edge("policy_guardrails", "reasoning_agent")
        graph_builder.add_edge("reasoning_agent", END)

        return graph_builder.compile()

    def _route_on_escalation(self, state: AgentState) -> Literal["escalated", "policy_check"]:
        if state["needs_escalation"]:
            return "escalated"
        return "policy_check"

    def _retriever_step(self, state: AgentState) -> AgentState:
        context = self.retriever.search(state["query"], top_k=3)
        trace = state.get("agent_trace", []) + ["retriever_agent"]
        return {**state, "retrieved_context": context, "agent_trace": trace}

    def _intent_classifier_step(self, state: AgentState) -> AgentState:
        classification = self.intent_classifier.classify(state["query"])
        trace = state.get("agent_trace", []) + ["intent_classifier"]
        return {
            **state,
            "intent": classification.intent,
            "confidence": classification.confidence,
            "agent_trace": trace,
        }

    def _escalation_evaluator_step(self, state: AgentState) -> AgentState:
        decision = self.escalation_evaluator.evaluate(
            state["query"],
            state["intent"],
            state["confidence"],
            state.get("retrieved_context", []),
        )
        trace = state.get("agent_trace", []) + ["escalation_evaluator"]
        return {
            **state,
            "needs_escalation": decision.needs_escalation,
            "escalation_reason": decision.reason if decision.needs_escalation else None,
            "agent_trace": trace,
        }

    def _policy_guardrails_step(self, state: AgentState) -> AgentState:
        check_result = self.policy_guardrails.check(state["query"], state["intent"])
        trace = state.get("agent_trace", []) + ["policy_guardrails"]
        return {
            **state,
            "policy_violations": check_result.violations,
            "agent_trace": trace,
        }

    def _reasoning_step(self, state: AgentState) -> AgentState:
        context = "\n".join(state.get("retrieved_context", []))
        intent = state.get("intent", "general")

        # Intent-specific prompt templates
        intent_prompts = {
            "billing": (
                "You are a billing support specialist. Be precise about fees, charges, and payment terms.\n"
            ),
            "shipping": (
                "You are a shipping support specialist. Provide accurate timelines and tracking information.\n"
            ),
            "account": (
                "You are an account support specialist. Focus on security, privacy, and account management.\n"
            ),
            "complaint": (
                "You are a complaints handler. Show empathy and work toward resolution.\n"
            ),
            "general": (
                "You are a customer support assistant.\n"
            ),
        }

        intent_prompt = intent_prompts.get(intent, intent_prompts["general"])

        # Add policy warnings if violations exist
        policy_note = ""
        if state.get("policy_violations"):
            policy_note = f"\nIMPORTANT POLICY NOTES:\n" + "\n".join(state["policy_violations"]) + "\n"

        prompt = (
            f"{intent_prompt}"
            f"Use the context when relevant.\n\n"
            f"Context:\n{context or 'No relevant context found.'}\n\n"
            f"{policy_note}"
            f"Customer Query:\n{state['query']}\n\n"
            "Provide a concise and helpful answer."
        )

        answer = self.llm.generate(prompt)
        trace = state.get("agent_trace", []) + ["reasoning_agent"]
        return {**state, "answer": answer, "agent_trace": trace}

    def run(self, query: str) -> AgentState:
        initial_state: AgentState = {
            "query": query,
            "retrieved_context": [],
            "intent": "general",
            "confidence": 0.0,
            "needs_escalation": False,
            "escalation_reason": None,
            "policy_violations": [],
            "answer": "",
            "agent_trace": [],
        }
        return self.graph.invoke(initial_state)
