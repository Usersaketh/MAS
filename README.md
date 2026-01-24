# MAS: Multi-Agent Customer Query System

Stage-by-stage build for a customer query processing system using:
- Ollama (LLM)
- LangGraph (multi-agent orchestration)
- FAISS (vector retrieval)
- FastAPI (backend API)

## Stage 5-lite (Interview Hardening)
Adds a minimal production-style layer without turning the project into a full deployment platform:

- API key authentication on all non-health endpoints
- Lightweight per-key rate limiting
- Existing multi-agent retrieval, memory, tracing, and tests kept intact

## Stage 4 (Still included)
Implemented a full multi-agent orchestration system with memory and observability:

1. Retriever Agent: fetches relevant context from FAISS vector DB
2. Memory Recall: loads recent turns for the current conversation
3. Intent Classifier Agent: classifies query intent with confidence score
4. Escalation Evaluator Agent: determines if query needs escalation
5. Policy Guardrails Agent: checks refund/cancellation policies and abuse patterns
6. Reasoning Agent: generates context-aware, intent-specific responses

Stage 4 additions:
- Conversation memory persisted per conversation ID
- Structured trace events persisted per query run
- Memory and trace retrieval APIs
- Unit tests for memory and graph behavior

### Project Structure

```text
app/
  api/routes/
    documents.py
    observability.py
    query.py
  core/config.py
  schemas/
    document.py
    query.py
  services/
    agent_graph.py
    llm_service.py
    memory_service.py
    retriever_service.py
    security.py
    runtime.py
    stage3_agents.py
    trace_service.py
  main.py
```

## Setup

1. Create virtual environment and install dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Copy env file and adjust if needed:

```powershell
Copy-Item .env.example .env
```

3. Start Ollama and ensure models are available:

```powershell
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve
```

4. Run API in another terminal:

```powershell
uvicorn app.main:app --reload
```

5. Provide the API key on requests:

```powershell
$headers = @{ "X-API-Key" = "dev-interview-key" }
Invoke-RestMethod -Method GET -Uri http://127.0.0.1:8000/health -Headers $headers
```

6. Test the query endpoint:

```powershell
$body = @{
    user_id = "u1"
    query = "Can I refund my order from last month?"
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/query -Headers $headers -ContentType "application/json" -Body $body
```

7. Ingest custom knowledge documents:

```powershell
$body = @{
    documents = @(
        "Premium support is available for enterprise customers.",
        "Order cancellation is possible within 30 minutes of placement."
    )
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/documents -Headers $headers -ContentType "application/json" -Body $body
```

8. Verify retriever status:

```powershell
Invoke-RestMethod -Method GET -Uri http://127.0.0.1:8000/documents/stats -Headers $headers
```

9. Inspect memory for a conversation:

```powershell
Invoke-RestMethod -Method GET -Uri http://127.0.0.1:8000/observability/conversations/u1/memory -Headers $headers
```

10. Inspect latest trace for a conversation:

```powershell
Invoke-RestMethod -Method GET -Uri http://127.0.0.1:8000/observability/conversations/u1/traces -Headers $headers
```

## Testing

Run the test suite with:

```powershell
pytest
```

## Next Stage
- Stage 5: Add production hardening (auth, rate limiting, retries, caching, dockerization)
