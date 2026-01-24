from __future__ import annotations

from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.services.llm_service import OllamaService
from app.services.retriever_service import RetrieverService


class AgentState(TypedDict):
    query: str
    retrieved_context: list[str]
    answer: str
    agent_trace: list[str]


class QueryAgentGraph:
    def __init__(self, retriever: RetrieverService, llm: OllamaService) -> None:
        self.retriever = retriever
        self.llm = llm
        self.graph = self._build_graph()

    def _build_graph(self):
        graph_builder = StateGraph(AgentState)

        graph_builder.add_node("retriever_agent", self._retriever_step)
        graph_builder.add_node("reasoning_agent", self._reasoning_step)

        graph_builder.set_entry_point("retriever_agent")
        graph_builder.add_edge("retriever_agent", "reasoning_agent")
        graph_builder.add_edge("reasoning_agent", END)

        return graph_builder.compile()

    def _retriever_step(self, state: AgentState) -> AgentState:
        context = self.retriever.search(state["query"], top_k=3)
        trace = state.get("agent_trace", []) + ["retriever_agent"]
        return {**state, "retrieved_context": context, "agent_trace": trace}

    def _reasoning_step(self, state: AgentState) -> AgentState:
        context = "\n".join(state.get("retrieved_context", []))
        prompt = (
            "You are a customer support assistant. Use the context when relevant.\n\n"
            f"Context:\n{context or 'No relevant context found.'}\n\n"
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
            "answer": "",
            "agent_trace": [],
        }
        return self.graph.invoke(initial_state)
