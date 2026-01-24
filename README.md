# MAS: Multi-Agent Customer Query System

Stage-by-stage build for a customer query processing system using:
- Ollama (LLM)
- LangGraph (multi-agent orchestration)
- FAISS (vector retrieval)
- FastAPI (backend API)

## Stage 3 (Current)
Implemented a full multi-agent orchestration system with specialized agents:

1. **Retriever Agent**: fetches relevant context from FAISS vector DB
2. **Intent Classifier Agent**: classifies query intent (billing, shipping, account, complaint, general) with confidence score
3. **Escalation Evaluator Agent**: determines if query needs escalation based on confidence and keywords
4. **Policy Guardrails Agent**: checks refund/cancellation policies and detects abuse patterns
5. **Reasoning Agent**: generates context-aware, intent-specific responses using specialized prompts

Stage 3 features:
- Multi-agent conditional routing based on escalation flags
- Intent-specific response generation
- Policy violation detection and reporting
- Confidence-based escalation thresholds
- Dynamic prompt adaptation per intent
- Full audit trail via agent_trace

### Project Structure

```text
app/
  api/routes/
    documents.py
    query.py
  core/config.py
  schemas/
    document.py
    query.py
  services/
    agent_graph.py
    llm_service.py
    retriever_service.py
    runtime.py
    stage3_agents.py
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

5. Test endpoint with a billing query:

```powershell
$body = @{
    user_id = "u1"
    query = "Can I refund my order from last month?"
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/query -ContentType "application/json" -Body $body
```

Expected response includes: intent, confidence, needs_escalation, escalation_reason, policy_violations.

6. Test endpoint with a complaint query (triggers escalation):

```powershell
$body = @{
    user_id = "u2"
    query = "I'm very angry! This is unfair and I demand a refund NOW!"
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/query -ContentType "application/json" -Body $body
```

7. Ingest custom knowledge documents:

```powershell
$body = @{
    documents = @(
        "Premium support is available for enterprise customers.",
        "Order cancellation is possible within 30 minutes of placement."
    )
} | ConvertTo-Json

Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/documents -ContentType "application/json" -Body $body
```

8. Verify retriever status:

```powershell
Invoke-RestMethod -Method GET -Uri http://127.0.0.1:8000/documents/stats
```

## Next Stages
- Stage 4: Add conversation memory, observability/tracing, and automated tests
- Stage 5: Add production hardening (auth, rate limiting, retries, caching, dockerization)
