# MAS: Multi-Agent Customer Query System

Stage-by-stage build for a customer query processing system using:
- Ollama (LLM)
- LangGraph (multi-agent orchestration)
- FAISS (vector retrieval)
- FastAPI (backend API)

## Stage 1 (Current)
Implemented foundational backend and a simple two-agent flow:
1. Retriever Agent: fetches relevant context from FAISS
2. Reasoning Agent: generates response with Ollama

### Project Structure

```text
app/
  api/routes/query.py
  core/config.py
  schemas/query.py
  services/
    agent_graph.py
    llm_service.py
    retriever_service.py
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

3. Start Ollama and ensure a model exists:

```powershell
ollama pull llama3.1:8b
ollama serve
```

4. Run API:

```powershell
uvicorn app.main:app --reload
```

5. Test endpoint:

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/query -ContentType "application/json" -Body '{"user_id":"u1","query":"How long does shipping take?"}'
```

## Next Stages
- Stage 2: Replace placeholder embeddings with real embedding model and persistent metadata store
- Stage 3: Add specialized agents (intent classification, escalation, policy checker)
- Stage 4: Add conversation memory, observability, and tests
- Stage 5: Add production hardening (auth, rate limiting, retries, caching)
