from app.services.agent_graph import QueryAgentGraph
from app.services.llm_service import OllamaService
from app.services.memory_service import ConversationMemoryService
from app.services.retriever_service import RetrieverService
from app.services.trace_service import TraceService

retriever = RetrieverService()
llm = OllamaService()
memory_service = ConversationMemoryService()
trace_service = TraceService()
agent_graph = QueryAgentGraph(retriever=retriever, llm=llm, memory_service=memory_service, trace_service=trace_service)
