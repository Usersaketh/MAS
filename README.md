# MAS: Multi-Agent Customer Query System

MAS is a simple final-project style demo that shows how a customer support assistant can combine retrieval, memory, classification, policy checks, and response generation.

## Overview

The system is split into two parts:

- Backend: FastAPI, LangGraph, FAISS, Ollama, Pydantic
- Frontend: React, TypeScript, Vite, Axios

The backend stores documents, conversation memory, and execution traces in `data/`, while the frontend provides a clean interface to ingest documents, ask questions, and inspect the agent flow.

## What It Does

- Accepts support documents and builds a vector index
- Classifies the user intent from a query
- Checks escalation and policy rules
- Uses conversation memory for follow-up context
- Returns a structured answer with trace information

## Project Structure

```text
.
├── app/                  # FastAPI backend
├── frontend/             # React + TypeScript UI
├── tests/                # Pytest test suite
├── sample-documents.json # Demo knowledge base documents
├── seed-data.py          # Seeds documents into the backend
└── requirements.txt
```

## Tech Stack

- FastAPI for the REST API
- LangGraph for the agent pipeline
- FAISS for similarity search
- Ollama for local LLM and embeddings
- React + TypeScript for the user interface

## Run the Project

### 1. Start Ollama

```powershell
ollama pull llama3.1:8b
ollama pull nomic-embed-text
ollama serve
```

### 2. Start the backend

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

Backend: http://localhost:8000

### 3. Start the frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```

Frontend: http://localhost:3000

## Demo Data

The repository includes `sample-documents.json`, a set of ready-made customer support documents covering:

- refunds and cancellations
- shipping and delivery
- billing and payments
- account security and verification
- returns, warranties, and loyalty programs

To seed them into the backend:

```powershell
python seed-data.py
```

The sample set has been expanded to make the demo more realistic and to improve retrieval quality during the interview presentation.

## How the Flow Works

1. A user submits a query in the UI.
2. The backend retrieves relevant document chunks from FAISS.
3. The intent classifier labels the request.
4. The escalation and policy agents apply business rules.
5. The reasoning agent generates the final response.
6. Memory and traces are stored for later inspection in the UI.

## Testing

Run the backend tests with:

```powershell
pytest -v
```

The suite covers memory handling, agent routing, API validation, and rate limiting.

## Notes

- Use the UI for the cleanest demo flow.
- The frontend is designed to show the data setup panel, query panel, and trace output in one place.
- The project is intentionally kept small and structured so it reads like a university final project rather than a production codebase.
2. Memory loads empty (first turn)
3. Intent = "complaint", confidence = 0.95 ✓
4. Escalation: confidence (0.95) > 0.6 ✓ + "ANGRY" keyword ✓ → **Escalate = TRUE**
5. **CONDITIONAL ROUTES TO END** (skip policy & reasoning)
6. Response: "Your request has been escalated to a human agent. We'll contact you within 2 hours."
7. Trace saved with 4 nodes executed, 2 skipped
8. Memory persisted

**Output:**
```json
{
  "conversation_id": "conv-u42-1",
  "answer": "Your request has been escalated...",
  "agent_trace": ["retriever_agent", "memory_recall", "intent_classifier", "escalation_evaluator"],
  "needs_escalation": true,
  "escalation_reason": "Query contains escalation indicators (anger, demands)",
  "trace_events": [
    {"step": "retriever_agent", "duration_ms": 15.2, "message": "Retrieved 3 context chunks"},
    ...
  ]
}
```

---

## Architecture Highlights

### Decoupled Services
- **RetrieverService**: FAISS + Ollama embedding, JSON persistence
- **LLMService**: Thin Ollama wrapper, easy to swap for OpenAI/Anthropic
- **MemoryService**: Per-conversation JSON storage with auto-truncation
- **TraceService**: Event logging with per-node timing
- **RateLimitService**: Thread-safe bucketing by (api_key + client_ip)

### Security (Stage 5-lite)
- **API Key Auth**: Header-based X-API-Key validation
- **Rate Limiting**: 30 requests/minute per key, sliding window with monotonic time
- **Dependency Injection**: FastAPI's `Depends()` for clean middleware

### Data Persistence
All files stored locally in `./data/`:
- `faiss.index` – Binary FAISS index
- `documents.json` – Document metadata
- `conversations.json` – Per-conversation turn history
- `traces.json` – Append-only trace events

### Type Safety
- Pydantic schemas for all request/response models
- TypeScript frontend with type-safe API client
- MyPy-compatible Python codebase

---

## Frontend Features

### QueryForm Component
- Textarea for multi-line customer questions
- Real-time loading state
- Error handling with user-friendly messages

### ResponseDisplay Component
- Agent response with intent badge
- Confidence score with color coding
- Escalation warning banner
- Retrieved context cards
- Agent trace visualization (node flow)
- Execution timeline (per-node duration)
- Conversation memory history (if available)

### DocumentManager Component
- Dynamic document input fields
- Bulk ingest with progress feedback
- Success/error states

### Stats Component
- FAISS index size display
- Document count
- Auto-refresh

---

## Configuration

Edit `.env` to customize:

```env
# Ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b
OLLAMA_EMBED_MODEL=nomic-embed-text

# Vector DB
VECTOR_DIMENSION=384
FAISS_INDEX_PATH=./data/faiss.index

# Agent Thresholds
ESCALATION_CONFIDENCE_THRESHOLD=0.6
MAX_REFUND_DAYS=30
MAX_CANCELLATION_MINUTES=30

# Memory & Tracing
MAX_MEMORY_TURNS=8

# Security
API_KEY=dev-interview-key
RATE_LIMIT_REQUESTS_PER_MINUTE=30
RATE_LIMIT_WINDOW_SECONDS=60
```

---

## Interview Tips

✅ **Show the full pipeline**: Submit a query, scroll through traces, explain each node  
✅ **Demonstrate escalation**: Ask an angry question to trigger early exit  
✅ **Show multi-turn memory**: Ask 2-3 related questions to show conversation context  
✅ **Explain the design**: Why LangGraph? Why per-conversation memory? Why FAISS?  
✅ **Highlight trade-offs**: JSON files for simplicity (not production-scale), local LLM (no API costs)  

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `Connection refused http://localhost:11434` | Ollama not running. Start with `ollama serve` |
| `FAISS dimension mismatch` | Delete `data/` folder and reingest documents |
| `Cannot find module 'react'` | Run `npm install` in `frontend/` directory |
| `API Key rejected` | Check `X-API-Key` header matches config value |
| `Rate limit exceeded` | Wait 60 seconds or adjust `RATE_LIMIT_REQUESTS_PER_MINUTE` |

---

## Next Steps (Production Hardening)

- [ ] Docker & docker-compose for easy deployment
- [ ] PostgreSQL for conversation/trace persistence (vs JSON)
- [ ] Redis for distributed rate limiting
- [ ] Structured logging (JSON logs, Datadog/ELK integration)
- [ ] Metrics (Prometheus, conversation success rate, avg latency)
- [ ] A/B testing framework for agent variants
- [ ] Caching layer (LLM responses by query hash)
- [ ] Async request queuing for high throughput

---

## License

MIT
