# MAS: Multi-Agent Customer Query System

Stage-by-stage build for a customer query processing system using:
- Ollama (LLM)
- LangGraph (multi-agent orchestration)
- FAISS (vector retrieval)
- FastAPI (backend API)

## Stage 2 (Current)
Implemented backend with real embedding-based retrieval and a two-agent flow:
1. Retriever Agent: fetches relevant context from FAISS
2. Reasoning Agent: generates response with Ollama

Stage 2 upgrades:
- Real embeddings via Ollama embedding model
- Persistent FAISS index on disk
- Persistent document metadata in JSON
- Document ingestion and retriever stats APIs

### Project Structure

```text
app/
  api/routes/documents.py
  api/routes/query.py
  core/config.py
  schemas/document.py
  schemas/query.py
  services/
    agent_graph.py
    llm_service.py
    runtime.py
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
ollama pull nomic-embed-text
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

6. Ingest your own knowledge documents:

```powershell
Invoke-RestMethod -Method POST -Uri http://127.0.0.1:8000/documents -ContentType "application/json" -Body '{"documents":["Premium support is available for enterprise customers.","Order cancellation is possible within 30 minutes of placement."]}'
```

7. Verify retriever status:

```powershell
Invoke-RestMethod -Method GET -Uri http://127.0.0.1:8000/documents/stats
```

## Next Stages
- Stage 3: Add specialized agents (intent classification, escalation, policy checker)
- Stage 4: Add conversation memory, observability, and tests
- Stage 5: Add production hardening (auth, rate limiting, retries, caching)
