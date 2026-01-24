from app.services.agent_graph import QueryAgentGraph
from app.services.llm_service import OllamaService
from app.services.retriever_service import RetrieverService

retriever = RetrieverService()
llm = OllamaService()
agent_graph = QueryAgentGraph(retriever=retriever, llm=llm)
